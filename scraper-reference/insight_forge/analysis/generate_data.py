"""
Generates a synthetic 'raw scraped' dataset that mimics what
market_intelligence_spider.py would land in S3 — including realistic dirt:
missing values, mixed timestamp formats, duplicate rows, out-of-range
metrics, and injected statistical outliers. Used to demonstrate/validate
the ingestion -> quality -> cleaning -> analysis pipeline end to end.
"""

import uuid
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

N = 1200
TENANTS = [str(uuid.uuid4()) for _ in range(4)]
SECTORS = ["Retail", "FMCG", "Automotive", "Fintech", "Healthcare", "EdTech"]
SOURCES = [
    "https://marketpulse.example.com/sector-index",
    "https://tradewatch.example.com/live-feed",
    "https://sectorscope.example.com/indicators",
]

date_range = pd.date_range("2026-05-01", "2026-06-30", freq="h")
timestamp_formats = [
    lambda d: d.strftime("%Y-%m-%dT%H:%M:%S"),
    lambda d: d.strftime("%d/%m/%Y %H:%M"),
    lambda d: d.strftime("%m-%d-%Y"),
    lambda d: d.strftime("%B %d, %Y %I:%M %p"),
]

rows = []
for i in range(N):
    tenant = rng.choice(TENANTS)
    sector = rng.choice(SECTORS)
    dt = pd.Timestamp(rng.choice(date_range))
    fmt = timestamp_formats[rng.integers(0, len(timestamp_formats))]

    metric = float(np.clip(rng.normal(0.55, 0.15), -0.1, 1.3))  # some out-of-range on purpose

    row = {
        "tenant_id": tenant,
        "source_url": rng.choice(SOURCES),
        "indicator_name": f"{sector.lower()}_demand_index",
        "indicator_metric": round(metric, 4),
        "temporal_stamp": fmt(dt),
        "sector": sector,
        "scraper_operator_email": f"operator{rng.integers(1, 6)}@datadragons.io",
        "submitted_by_ip": f"10.{rng.integers(0,255)}.{rng.integers(0,255)}.{rng.integers(0,255)}",
    }
    rows.append(row)

df = pd.DataFrame(rows)

# Inject missing values (~8% of indicator_metric, ~5% of temporal_stamp, ~4% of sector)
for col, frac in [("indicator_metric", 0.08), ("temporal_stamp", 0.05), ("sector", 0.04)]:
    idx = df.sample(frac=frac, random_state=1).index
    df.loc[idx, col] = np.nan

# Inject a handful of duplicate rows
dupes = df.sample(n=25, random_state=2)
df = pd.concat([df, dupes], ignore_index=True)

# Inject some extreme statistical outliers
outlier_idx = df.sample(n=15, random_state=3).index
df.loc[outlier_idx, "indicator_metric"] = rng.choice([2.5, -1.8, 3.1, -2.0], size=len(outlier_idx))

df = df.sample(frac=1.0, random_state=7).reset_index(drop=True)
df.to_csv("/home/claude/insight_forge/analysis/raw_scraped_landing.csv", index=False)
print(f"Generated {len(df)} raw scraped rows -> analysis/raw_scraped_landing.csv")
