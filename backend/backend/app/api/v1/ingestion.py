"""Ingestion endpoint — streamed file upload into a dataset + records."""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.core.errors import AppError
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, ensure_sector, get_current_user
from app.db.session import get_db
from app.schemas.ingestion import IngestionResponse

router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


@router.post(
    "/stream",
    response_model=IngestionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def stream_upload(
    sector: str = Form(...),
    file: UploadFile = File(...),
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IngestionResponse:
    import os
    import uuid
    from app.core.config import settings
    from app.models.dataset import Dataset
    from app.models.enums import DatasetProcessingStatus, DatasetStatus
    from app.tasks.ingestion import ingest_dataset_task

    workspace_id = ensure_sector(current, sector)

    # 1. Save uploaded file safely
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
    temp_filename = f"{uuid.uuid4()}_{file.filename or 'upload.csv'}"
    temp_path = os.path.join(settings.UPLOAD_DIRECTORY, temp_filename)

    file_size = 0
    with open(temp_path, "wb") as f:
        while chunk := await file.read(8192):
            f.write(chunk)
            file_size += len(chunk)

    # 2. Create Dataset entry with status PENDING (which maps to queued)
    dataset = Dataset(
        organization_id=current.organization_id,
        workspace_id=workspace_id,
        uploaded_by=current.id,
        name=file.filename or "upload",
        file_name=file.filename or "upload",
        file_type=file.content_type or "application/octet-stream",
        storage_path=temp_path,
        file_size=file_size,
        total_rows=0,
        total_columns=0,
        processing_status=DatasetProcessingStatus.PENDING,
        status=DatasetStatus.ACTIVE,
        created_by=current.id,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # 3. Dispatch Celery Task (fall back to background thread if broker unavailable)
    try:
        ingest_dataset_task.delay(
            str(dataset.id),
            temp_path,
            str(current.organization_id),
            str(workspace_id),
            str(current.id),
        )
    except Exception:
        # No Celery broker available — run in a daemon background thread so the
        # 202 Accepted response returns immediately without blocking the request.
        import threading
        t = threading.Thread(
            target=ingest_dataset_task,
            args=(
                str(dataset.id),
                temp_path,
                str(current.organization_id),
                str(workspace_id),
                str(current.id),
            ),
            daemon=True,
        )
        t.start()

    return IngestionResponse(
        dataset_id=str(dataset.id),
        sector=sector,
        status=dataset.processing_status.value,
        size_bytes=dataset.file_size,
        message="Dataset upload accepted and queued for processing",
    )
