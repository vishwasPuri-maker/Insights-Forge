"""Ingestion route: streaming multipart upload to the S3 landing bucket.

This endpoint stores the raw file and triggers the separate cleaning worker.
It does NOT parse or clean the data (that's the Data Analyst's service). The
file streams to S3 in ~1 MB parts; the response returns the new dataset_id so
the frontend can poll /datasets/{id} for cleaning status + health score.
"""
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.auth.jwt_handler import TokenData, require_role
from app.database import get_db, set_organization_context
from app.models import Dataset
from app.schemas import ALLOWED_SECTORS, IngestionResponse
from app.services.cleaning_trigger import trigger_cleaning
from app.storage import build_object_key, stream_to_landing

router = APIRouter(prefix="/ingestion", tags=["ingestion"])


@router.post("/stream", response_model=IngestionResponse, status_code=status.HTTP_201_CREATED)
def stream_upload(
    background: BackgroundTasks,
    sector: str = Form(...),
    file: UploadFile = File(...),
    # Only manager/admin may ingest data; plain `user` is read-only.
    current: TokenData = Depends(require_role("manager", "admin")),
    db: Session = Depends(get_db),
) -> IngestionResponse:
    if sector not in ALLOWED_SECTORS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "invalid_sector", "message": f"sector must be one of {sorted(ALLOWED_SECTORS)}"},
        )
    # A user is fixed to one sector; they may only ingest into their own.
    if sector != current.sector:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "sector_forbidden", "message": "cannot ingest into another sector"},
        )

    set_organization_context(db, current.organization_id)

    dataset_id = uuid.uuid4()
    key = build_object_key(current.organization_id, str(dataset_id), file.filename or "upload")
    dataset = Dataset(
        id=dataset_id,
        organization_id=uuid.UUID(current.organization_id),
        uploaded_by=uuid.UUID(current.user_id),
        sector=sector,
        original_filename=file.filename or "upload",
        s3_key=key,
        content_type=file.content_type,
        status="pending",
    )
    db.add(dataset)
    db.flush()

    try:
        size = stream_to_landing(file.file, key, file.content_type)
    except Exception:
        dataset.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"code": "upload_failed", "message": "could not store the uploaded file"},
        )

    dataset.size_bytes = size
    dataset.status = "uploaded"
    db.commit()

    # Hand off to the external cleaning worker after the response is sent.
    background.add_task(
        trigger_cleaning, str(dataset_id), key, sector, current.organization_id
    )

    return IngestionResponse(
        dataset_id=str(dataset_id), sector=sector, status=dataset.status, size_bytes=size
    )
