# /spark/scripts/clean_and_score.py
# Task 3: Airflow Ingestion Workflow & Autonomous PySpark Sanitization Core
# Mapping: Doc 6 (IMP Section 2 - Feature 1), Doc 2 (TRD Section 9.2)
"""
Multi-threaded statistical cleaning & health-scoring job.

- Normalizes variant temporal formats to ISO 8601.
- Drops any partition where row corruption exceeds C > 30%.
- Flags statistical outliers out-of-band using IsolationForest.
- Imputes missing numeric telemetry with KNNImputer.
- Hashes PII fields with SHA-256 before the data lands in analytics layers.
"""

from __future__ import annotations

import hashlib
import sys

import pandas as pd
from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import pyspark.sql.types as T
from sklearn.ensemble import IsolationForest
from sklearn.impute import KNNImputer

CORRUPTION_DROP_THRESHOLD = 0.30
PII_FIELDS = ["scraper_operator_email", "submitted_by_ip"]


def sha256_hash(value):
    if value is None:
        return None
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


sha256_udf = F.udf(sha256_hash, T.StringType())


def _corruption_ratio(df) -> float:
    total = df.count()
    if total == 0:
        return 0.0
    corrupt = df.filter(
        F.col("indicator_metric").isNull() | F.col("temporal_stamp").isNull()
    ).count()
    return corrupt / total


def _flag_outliers_pandas(pdf: pd.DataFrame) -> pd.DataFrame:
    """Runs per-tenant partition through IsolationForest + KNNImputer locally."""
    if pdf.empty:
        pdf["is_outlier"] = pd.Series(dtype=bool)
        return pdf

    numeric_cols = ["indicator_metric"]

    # KNNImputer fills missing telemetry using nearest-neighbor similarity
    imputer = KNNImputer(n_neighbors=min(5, max(1, len(pdf) - 1)))
    pdf[numeric_cols] = imputer.fit_transform(pdf[numeric_cols])

    # IsolationForest flags statistical noise out-of-band (does not drop rows,
    # only tags them for downstream review per Doc 2 TRD Section 9.2).
    forest = IsolationForest(contamination=0.05, random_state=42)
    pdf["is_outlier"] = forest.fit_predict(pdf[numeric_cols]) == -1
    return pdf


def clean_telemetry_stream(input_path: str, output_path: str) -> None:
    spark = SparkSession.builder.appName("InsightForgeSanitization").getOrCreate()

    df = spark.read.parquet(input_path)

    # Coerce temporal variants into unified ISO 8601 stamps
    sanitized_df = df.withColumn("temporal_stamp", F.to_timestamp("temporal_stamp"))

    # Guardrail: drop the whole batch if structural corruption crosses 30%
    corruption = _corruption_ratio(sanitized_df)
    if corruption > CORRUPTION_DROP_THRESHOLD:
        print(f"Corruption ratio {corruption:.2%} exceeds threshold — batch dropped.")
        spark.stop()
        return

    # Hash PII before it lands in downstream analytics layers
    for field in PII_FIELDS:
        if field in sanitized_df.columns:
            sanitized_df = sanitized_df.withColumn(field, sha256_udf(F.col(field)))

    # Per-tenant statistical cleaning: apply pandas UDF grouped by tenant_id
    schema = sanitized_df.schema.add(T.StructField("is_outlier", T.BooleanType()))

    cleaned_df = sanitized_df.groupBy("tenant_id").applyInPandas(
        _flag_outliers_pandas, schema=schema
    )

    cleaned_df.write.partitionBy("tenant_id").mode("append").parquet(output_path)
    spark.stop()


if __name__ == "__main__":
    clean_telemetry_stream(sys.argv[1], sys.argv[2])
