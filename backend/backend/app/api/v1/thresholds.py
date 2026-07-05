"""Threshold endpoints — list + update, scoped to the caller's workspace."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, lazyload

from app.api.deps import CurrentUser, get_current_user, require_roles
from app.core.errors import AppError
from app.db.session import get_db
from app.models.threshold import Threshold
from app.schemas.threshold import ThresholdOut, ThresholdUpdate

router = APIRouter(prefix="/thresholds", tags=["Thresholds"])


def to_out(t: Threshold, sector: str) -> ThresholdOut:
    return ThresholdOut(
        id=t.id,
        sector=sector,
        metric_key=t.metric_key,
        label=t.label,
        warning_value=float(t.warning_value) if t.warning_value is not None else None,
        critical_value=(
            float(t.critical_value) if t.critical_value is not None else None
        ),
    )


@router.get("", response_model=list[ThresholdOut])
def list_thresholds(
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ThresholdOut]:
    stmt = (
        select(Threshold)
        .where(
            Threshold.workspace_id == current.workspace_id,
            Threshold.is_deleted.is_(False),
        )
        .order_by(Threshold.metric_key)
        .options(lazyload("*"))
    )
    return [to_out(t, current.sector) for t in db.execute(stmt).scalars().all()]


@router.put("/{threshold_id}", response_model=ThresholdOut)
def update_threshold(
    threshold_id: uuid.UUID,
    payload: ThresholdUpdate,
    current: CurrentUser = Depends(require_roles("admin", "manager")),
    db: Session = Depends(get_db),
) -> ThresholdOut:
    t = db.get(Threshold, threshold_id, options=[lazyload("*")])
    if t is None or t.is_deleted or t.workspace_id != current.workspace_id:
        raise AppError(404, "not_found", "Threshold not found")
    t.warning_value = payload.warning_value
    t.critical_value = payload.critical_value
    db.commit()
    return to_out(t, current.sector)
