# /dags/ingestion_processing_dag.py
# Task 3: Airflow Ingestion Workflow & Autonomous PySpark Sanitization Core
# Mapping: Doc 6 (IMP Section 2 - Feature 1), Doc 2 (TRD Section 9.2)
"""
Master ingestion & sanitization DAG. Triggered by S3 landing events on the
tenant raw prefix. Runs the PySpark cleaning/health-scoring job and emits
Prometheus-visible run metadata on completion.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator

DEFAULT_ARGS = {
    "owner": "data-dragons",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

TENANT_PREFIX = "tenants/{{ params.tenant_id }}/raw/*.csv"

with DAG(
    dag_id="ingestion_processing_dag",
    description="Insight Forge multi-tenant ingestion & sanitization pipeline",
    default_args=DEFAULT_ARGS,
    schedule=None,  # event-driven: triggered by the S3 sensor below
    start_date=datetime(2026, 1, 1),
    catchup=False,
    params={"tenant_id": ""},
    tags=["insight-forge", "ingestion", "data-dragons"],
) as dag:

    wait_for_landing_file = S3KeySensor(
        task_id="wait_for_landing_file",
        bucket_name="insightforge-data-lake-prod",
        bucket_key=TENANT_PREFIX,
        wildcard_match=True,
        aws_conn_id="aws_default",
        poke_interval=60,
        timeout=60 * 60 * 6,
        mode="reschedule",
    )

    def _verify_tenant_isolation(**context):
        """Guardrail: refuse to proceed if tenant_id param is missing."""
        tenant_id = context["params"].get("tenant_id")
        if not tenant_id:
            raise ValueError("tenant_id must be supplied — cross-tenant runs are forbidden.")
        return tenant_id

    verify_tenant_isolation = PythonOperator(
        task_id="verify_tenant_isolation",
        python_callable=_verify_tenant_isolation,
    )

    run_pyspark_sanitization = SparkSubmitOperator(
        task_id="run_pyspark_sanitization",
        application="/spark/scripts/clean_and_score.py",
        application_args=[
            "s3a://insightforge-data-lake-prod/tenants/{{ params.tenant_id }}/raw/",
            "s3a://insightforge-data-lake-prod/tenants/{{ params.tenant_id }}/clean/",
        ],
        conn_id="spark_default",
        conf={"spark.sql.shuffle.partitions": "8"},
    )

    def _log_run_metrics(**context):
        """Push a structural run record for Prometheus scraping / audit trail."""
        print(
            {
                "dag_id": "ingestion_processing_dag",
                "tenant_id": context["params"].get("tenant_id"),
                "run_ts": context["ts"],
                "status": "completed",
            }
        )

    log_run_metrics = PythonOperator(
        task_id="log_run_metrics",
        python_callable=_log_run_metrics,
    )

    wait_for_landing_file >> verify_tenant_isolation >> run_pyspark_sanitization >> log_run_metrics
