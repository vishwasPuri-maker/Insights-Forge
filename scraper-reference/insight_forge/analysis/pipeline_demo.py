"""
End-to-end local demonstration of the Insight Forge ingestion pipeline,
mirroring the logic in validation_schema.py and clean_and_score.py, run
against the synthetic raw_scraped_landing.csv dataset.

Stages:
  1. Data Ingestion
  2. Data Quality Assessment
  3. Data Cleaning
  4. Descriptive Statistics
  5. Univariate Analysis
  6. Bivariate Analysis

Outputs: JSON summary + PNG charts in ./charts/
"""

import hashlib
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.impute import KNNImputer

sys.path.insert(0, "/home/claude/insight_forge/scraper")
from validation_schema import score_structural_completeness, DEAD_LETTER_THRESHOLD  # noqa: E402

plt.rcParams.update({"figure.dpi": 130, "font.size": 10, "axes.grid": True, "grid.alpha": 0.3})
CHART_DIR = "/home/claude/insight_forge/analysis/charts"
COLOR = "#3b5bdb"
COLOR2 = "#f76707"

summary = {}

# =========================================================================
# 1. DATA INGESTION
# =========================================================================
raw = pd.read_csv("/home/claude/insight_forge/analysis/raw_scraped_landing.csv")
summary["ingestion"] = {
    "rows_landed": len(raw),
    "distinct_tenants": raw["tenant_id"].nunique(),
    "distinct_sources": raw["source_url"].nunique(),
    "date_range_note": "Simulated S3 landing at tenants/<tenant_uuid>/raw/",
}

# =========================================================================
# 2. DATA QUALITY ASSESSMENT
# =========================================================================
required = ["tenant_id", "source_url", "indicator_name", "indicator_metric", "temporal_stamp"]
raw["_completeness_score"] = raw.apply(
    lambda r: score_structural_completeness(r[required].to_dict()), axis=1
)
raw["_valid"] = raw["_completeness_score"] >= DEAD_LETTER_THRESHOLD
raw["_out_of_range"] = ~raw["indicator_metric"].between(0.0, 1.0)
raw["_duplicate"] = raw.duplicated(subset=required, keep="first")

n_total = len(raw)
n_deadletter = int((~raw["_valid"]).sum())
n_out_of_range = int(raw["_out_of_range"].sum())
n_duplicate = int(raw["_duplicate"].sum())
missing_pct = raw[["indicator_metric", "temporal_stamp", "sector"]].isna().mean().round(4) * 100

summary["quality_assessment"] = {
    "total_rows": n_total,
    "rows_below_completeness_threshold_deadletter": n_deadletter,
    "rows_out_of_logical_range": n_out_of_range,
    "duplicate_rows": n_duplicate,
    "missing_pct_by_column": missing_pct.to_dict(),
    "corruption_ratio_pct": round(
        raw[["indicator_metric", "temporal_stamp"]].isna().any(axis=1).mean() * 100, 2
    ),
}

fig, ax = plt.subplots(figsize=(6, 4))
missing_pct.plot(kind="bar", ax=ax, color=COLOR)
ax.set_ylabel("% Missing")
ax.set_title("Data Quality: Missingness by Field (Raw Landing)")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/01_quality_missingness.png")
plt.close()

fig, ax = plt.subplots(figsize=(5, 5))
labels = ["Valid", "Dead-letter\n(< 70% complete)"]
sizes = [n_total - n_deadletter, n_deadletter]
ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=[COLOR, COLOR2], startangle=90)
ax.set_title("Structural Validation Outcome")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/02_quality_validation_split.png")
plt.close()

# =========================================================================
# 3. DATA CLEANING
# =========================================================================
clean = raw[raw["_valid"] & ~raw["_duplicate"]].copy()

# Normalize temporal_stamp to ISO 8601 — try each known scraped format explicitly
# before falling back to pandas' general inference (mirrors real multi-source dirt).
KNOWN_FORMATS = ["%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M", "%m-%d-%Y", "%B %d, %Y %I:%M %p"]


def _parse_temporal(value):
    if pd.isna(value):
        return pd.NaT
    for fmt in KNOWN_FORMATS:
        try:
            return pd.to_datetime(value, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.to_datetime(value, errors="coerce")


clean["temporal_stamp_parsed"] = clean["temporal_stamp"].apply(_parse_temporal)
unparseable = int(clean["temporal_stamp_parsed"].isna().sum())
clean = clean.dropna(subset=["temporal_stamp_parsed"])

# KNN-impute missing indicator_metric, sector left as "Unknown"
before_missing = int(clean["indicator_metric"].isna().sum())
imputer = KNNImputer(n_neighbors=5)
clean["indicator_metric"] = imputer.fit_transform(clean[["indicator_metric"]])
clean["sector"] = clean["sector"].fillna("Unknown")

# Clip / flag out-of-range values (logical bound is [0,1] per schema)
clean["_range_flag"] = ~clean["indicator_metric"].between(0.0, 1.0)

# IsolationForest outlier flagging (out-of-band, not dropped)
forest = IsolationForest(contamination=0.05, random_state=42)
clean["is_outlier"] = forest.fit_predict(clean[["indicator_metric"]]) == -1

# PII hashing
for col in ["scraper_operator_email", "submitted_by_ip"]:
    clean[col + "_hashed"] = clean[col].apply(
        lambda v: hashlib.sha256(str(v).encode()).hexdigest()[:16]
    )

clean_final = clean[clean["indicator_metric"].between(-2, 3)]  # sanity guard, keeps flagged outliers visible

summary["cleaning"] = {
    "rows_after_validation_and_dedup": len(raw[raw["_valid"] & ~raw["_duplicate"]]),
    "rows_dropped_unparseable_timestamp": unparseable,
    "rows_knn_imputed_indicator_metric": before_missing,
    "rows_flagged_as_statistical_outliers": int(clean["is_outlier"].sum()),
    "rows_out_of_logical_range_after_clean": int(clean["_range_flag"].sum()),
    "final_clean_row_count": len(clean),
    "pii_fields_hashed": ["scraper_operator_email", "submitted_by_ip"],
}

clean.to_csv("/home/claude/insight_forge/analysis/cleaned_dataset.csv", index=False)

fig, ax = plt.subplots(figsize=(6, 4))
stages = ["Raw\nLanded", "Valid &\nDeduped", "Timestamp\nParsed", "Final\nCleaned"]
counts = [
    n_total,
    len(raw[raw["_valid"] & ~raw["_duplicate"]]),
    len(raw[raw["_valid"] & ~raw["_duplicate"]]) - unparseable,
    len(clean),
]
ax.bar(stages, counts, color=[COLOR, COLOR, COLOR, "#2f9e44"])
for i, c in enumerate(counts):
    ax.text(i, c + 8, str(c), ha="center")
ax.set_ylabel("Row Count")
ax.set_title("Pipeline Funnel: Rows Surviving Each Cleaning Stage")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/03_cleaning_funnel.png")
plt.close()

# =========================================================================
# 4. DESCRIPTIVE STATISTICS  (on cleaned data)
# =========================================================================
desc = clean["indicator_metric"].describe().round(4)
summary["descriptive_statistics"] = {
    "indicator_metric": desc.to_dict(),
    "sector_value_counts": clean["sector"].value_counts().to_dict(),
    "tenant_row_counts": clean["tenant_id"].value_counts().round(2).to_dict(),
}

# =========================================================================
# 5. UNIVARIATE ANALYSIS
# =========================================================================
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].hist(clean["indicator_metric"], bins=30, color=COLOR, edgecolor="white")
axes[0].axvline(clean["indicator_metric"].mean(), color=COLOR2, linestyle="--", label="mean")
axes[0].set_title("Univariate: Indicator Metric Distribution")
axes[0].set_xlabel("indicator_metric")
axes[0].legend()

clean["sector"].value_counts().plot(kind="bar", ax=axes[1], color=COLOR)
axes[1].set_title("Univariate: Record Count by Sector")
axes[1].set_xlabel("")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/04_univariate_metric_sector.png")
plt.close()

fig, ax = plt.subplots(figsize=(6, 4))
ax.boxplot(clean["indicator_metric"], vert=False)
ax.set_title("Univariate: Indicator Metric Spread (Boxplot)")
ax.set_xlabel("indicator_metric")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/05_univariate_boxplot.png")
plt.close()

# =========================================================================
# 6. BIVARIATE ANALYSIS
# =========================================================================
fig, ax = plt.subplots(figsize=(7, 4.5))
clean.boxplot(column="indicator_metric", by="sector", ax=ax, patch_artist=True,
              boxprops=dict(facecolor=COLOR, alpha=0.6))
ax.set_title("Bivariate: Indicator Metric by Sector")
ax.set_xlabel("Sector")
ax.set_ylabel("indicator_metric")
plt.suptitle("")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/06_bivariate_metric_by_sector.png")
plt.close()

clean["hour"] = clean["temporal_stamp_parsed"].dt.hour
hourly = clean.groupby("hour")["indicator_metric"].mean()
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(hourly.index, hourly.values, marker="o", color=COLOR)
ax.set_title("Bivariate: Mean Indicator Metric by Hour of Day")
ax.set_xlabel("Hour")
ax.set_ylabel("Mean indicator_metric")
plt.tight_layout()
plt.savefig(f"{CHART_DIR}/07_bivariate_metric_by_hour.png")
plt.close()

sector_outlier_rate = clean.groupby("sector")["is_outlier"].mean().sort_values(ascending=False) * 100
summary["bivariate_analysis"] = {
    "mean_metric_by_sector": clean.groupby("sector")["indicator_metric"].mean().round(4).to_dict(),
    "outlier_rate_pct_by_sector": sector_outlier_rate.round(2).to_dict(),
    "correlation_hour_vs_metric": round(
        clean[["hour", "indicator_metric"]].corr().iloc[0, 1], 4
    ),
}

with open("/home/claude/insight_forge/analysis/pipeline_summary.json", "w") as f:
    json.dump(summary, f, indent=2, default=str)

print(json.dumps(summary, indent=2, default=str))
