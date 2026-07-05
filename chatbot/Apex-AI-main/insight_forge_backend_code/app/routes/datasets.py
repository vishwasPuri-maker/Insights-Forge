"""Dataset routes: list uploaded datasets and fetch one by id.

Read-only and open to any authenticated role. Every query runs under the
organization's RLS context; we also filter by organization_id explicitly as
defense in depth (never rely on either mechanism alone).
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.jwt_handler import TokenData, get_current_user
from app.database import get_db, set_organization_context
from app.models import Dataset
from app.schemas import DatasetOut

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=list[DatasetOut])
def list_datasets(
    current: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[Dataset]:
    set_organization_context(db, current.organization_id)
    return list(
        db.scalars(
            select(Dataset)
            .where(Dataset.organization_id == uuid.UUID(current.organization_id))
            .order_by(Dataset.created_at.desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(
    dataset_id: uuid.UUID,
    current: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dataset:
    set_organization_context(db, current.organization_id)
    dataset = db.scalar(
        select(Dataset).where(
            Dataset.id == dataset_id,
            Dataset.organization_id == uuid.UUID(current.organization_id),
        )
    )
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "dataset not found"},
        )
    return dataset
