import os
import uuid
import logging
import traceback
from datetime import datetime, timezone
from celery import shared_task

from app.db.session import SessionLocal
from app.models.dataset import Dataset
from app.models.enums import DatasetProcessingStatus, DatasetStatus
from app.models.record import Record
from app.services.ingestion_service import _rows_from_bytes, _extract_recorded_at

logger = logging.getLogger("celery-worker")


@shared_task(
    name="app.tasks.ingestion.ingest_dataset_task", max_retries=3, default_retry_delay=5
)
def ingest_dataset_task(
    dataset_id_str: str,
    file_path: str,
    organization_id_str: str,
    workspace_id_str: str,
    user_id_str: str,
) -> bool:
    """
    Celery task that reads the uploaded CSV file from disk, validates and parses
    it, inserts records in bulk, and updates the Dataset processing status.
    """
    logger.info(f"Starting background ingestion for dataset {dataset_id_str}")

    dataset_id = uuid.UUID(dataset_id_str)
    organization_id = uuid.UUID(organization_id_str)
    workspace_id = uuid.UUID(workspace_id_str)
    uuid.UUID(user_id_str)

    db = SessionLocal()
    try:
        # 1. Update status to PROCESSING
        dataset = db.get(Dataset, dataset_id)
        if not dataset:
            logger.error(f"Dataset {dataset_id_str} not found in database.")
            return False

        dataset.processing_status = DatasetProcessingStatus.PROCESSING
        db.commit()

        # 2. Read stored file from disk
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Stored dataset file not found at: {file_path}")

        with open(file_path, "rb") as f:
            raw = f.read()

        # 3. Parse and extract rows
        rows = _rows_from_bytes(raw, dataset.file_name, dataset.file_type)

        if not rows:
            raise ValueError(
                f"File '{dataset.file_name}' produced zero parseable rows. "
                "Please check the file format and content."
            )

        total_columns = len(rows[0]) if rows else 0

        dataset.total_rows = len(rows)
        dataset.total_columns = total_columns

        # 4. Insert records
        now = datetime.now(timezone.utc)
        for row in rows:
            db.add(
                Record(
                    organization_id=organization_id,
                    workspace_id=workspace_id,
                    dataset_id=dataset.id,
                    data=row,
                    recorded_at=_extract_recorded_at(row) or now,
                )
            )

        # 5. Transition to COMPLETED
        dataset.processing_status = DatasetProcessingStatus.COMPLETED
        dataset.status = DatasetStatus.ACTIVE
        db.commit()

        # Dispatch event for background indexing
        try:
            from app.core.rag.events import RAGEventDispatcher, RAGEvent

            RAGEventDispatcher.dispatch(
                RAGEvent.DATASET_COMPLETED, {"dataset_id": dataset_id_str}
            )
        except Exception as e_event:
            logger.error(f"Failed to dispatch RAG completed event: {str(e_event)}")

        logger.info(
            f"Ingestion completed successfully for dataset {dataset_id_str}. Ingested {len(rows)} rows."
        )

        # 6. Clean up temporary file from UPLOAD_DIRECTORY
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Temporary file {file_path} deleted successfully.")
        except Exception as cleanup_err:
            logger.warning(
                f"Failed to delete temporary file {file_path}: {str(cleanup_err)}"
            )

        return True

    except Exception as e:
        error_msg = f"Error processing dataset {dataset_id_str}: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())

        # Rollback current transaction and save failure state to dataset
        db.rollback()
        try:
            dataset = db.get(Dataset, dataset_id)
            if dataset:
                dataset.processing_status = DatasetProcessingStatus.FAILED
                # Persist the failure description in the description field
                dataset.description = f"Ingestion failed: {str(e)}"
                db.commit()
        except Exception as status_err:
            logger.error(
                f"Failed to update dataset status to FAILED: {str(status_err)}"
            )

        db.close()
        raise e
    finally:
        db.close()
