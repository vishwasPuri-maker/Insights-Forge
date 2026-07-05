"""Hand-off to the separate cleaning worker.

IMPORTANT: data cleaning / ML is NOT this repo's job (that's the Data Analyst's
service). This function only *notifies* / enqueues the external worker with a
pointer to the landed file. It must never import pandas/scikit-learn or process
the data itself. Runs via FastAPI BackgroundTasks — not Celery.
"""
import logging

logger = logging.getLogger("decisiq.ingestion")


def trigger_cleaning(dataset_id: str, s3_key: str, sector: str, organization_id: str) -> None:
    """Notify the cleaning worker that a new raw file is ready to process.

    TODO: replace this stub with the real hand-off (POST to the worker's endpoint
    or drop a message on its queue). Kept as a no-op log so the ingestion slice
    works end-to-end without owning any cleaning logic.
    """
    logger.info(
        "cleaning hand-off queued: dataset=%s organization=%s sector=%s key=%s",
        dataset_id,
        organization_id,
        sector,
        s3_key,
    )
