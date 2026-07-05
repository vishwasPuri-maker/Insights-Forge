"""Dataset endpoints — list + fetch, scoped to the caller's workspace."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, lazyload

from app.api.deps import CurrentUser, get_current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetOut

router = APIRouter(prefix="/datasets", tags=["Datasets"])


def to_out(dataset: Dataset, sector: str) -> DatasetOut:
    return DatasetOut(
        id=dataset.id,
        sector=sector,
        original_filename=dataset.file_name,
        status=dataset.processing_status.value,
        health_score=None,
        size_bytes=dataset.file_size,
        content_type=dataset.file_type,
        uploaded_by=dataset.uploaded_by,
        created_at=dataset.created_at,
        total_rows=dataset.total_rows,
        description=dataset.description,
    )


@router.get("", response_model=list[DatasetOut])
def list_datasets(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DatasetOut]:
    stmt = (
        select(Dataset)
        .where(
            Dataset.workspace_id == current.workspace_id,
            Dataset.is_deleted.is_(False),
        )
        .order_by(Dataset.created_at.desc())
        .limit(limit)
        .offset(offset)
        .options(lazyload("*"))
    )
    return [to_out(d, current.sector) for d in db.execute(stmt).scalars().all()]


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(
    dataset_id: uuid.UUID,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DatasetOut:
    dataset = db.get(Dataset, dataset_id, options=[lazyload("*")])
    if (
        dataset is None
        or dataset.is_deleted
        or dataset.workspace_id != current.workspace_id
    ):
        raise AppError(404, "not_found", "Dataset not found")
    return to_out(dataset, current.sector)
