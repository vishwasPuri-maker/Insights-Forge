"""KPI threshold config: GET /thresholds and PUT /thresholds/{id}.

Thresholds are org- and sector-scoped. Reading is open to any authenticated role
(dashboards render them); editing requires `manager` or `admin` (RBAC). Every
query runs under the organization's RLS context + explicit organization_id filter.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.jwt_handler import TokenData, get_current_user, require_role
from app.database import get_db, set_organization_context
from app.models import KpiThreshold
from app.schemas import ThresholdOut, ThresholdUpdate

router = APIRouter(prefix="/thresholds", tags=["thresholds"])


@router.get("", response_model=list[ThresholdOut])
def list_thresholds(
    current: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[KpiThreshold]:
    set_organization_context(db, current.organization_id)
    return list(
        db.scalars(
            select(KpiThreshold)
            .where(
                KpiThreshold.organization_id == uuid.UUID(current.organization_id),
                KpiThreshold.sector == current.sector,
            )
            .order_by(KpiThreshold.metric_key)
        ).all()
    )


@router.put("/{threshold_id}", response_model=ThresholdOut)
def update_threshold(
    threshold_id: uuid.UUID,
    body: ThresholdUpdate,
    current: TokenData = Depends(require_role("manager", "admin")),
    db: Session = Depends(get_db),
) -> KpiThreshold:
    set_organization_context(db, current.organization_id)
    threshold = db.scalar(
        select(KpiThreshold).where(
            KpiThreshold.id == threshold_id,
            KpiThreshold.organization_id == uuid.UUID(current.organization_id),
            KpiThreshold.sector == current.sector,
        )
    )
    if threshold is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "threshold not found"},
        )
    threshold.warning_value = body.warning_value
    threshold.critical_value = body.critical_value
    db.commit()
    db.refresh(threshold)
    return threshold
