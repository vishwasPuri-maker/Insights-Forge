"""Decision-card endpoints, backed by ai_recommendations (per contract mapping)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, lazyload

from app.api.deps import CurrentUser, get_current_user, require_roles
from app.core.errors import AppError
from app.db.session import get_db
from app.models.ai_recommendation import AIRecommendation
from app.models.enums import DecisionStatus
from app.schemas.decision import DecisionCardOut

router = APIRouter(prefix="/decision-cards", tags=["Decision Cards"])


def to_out(rec: AIRecommendation, sector: str) -> DecisionCardOut:
    return DecisionCardOut(
        id=rec.id,
        sector=sector,
        title=rec.title
        or (
            rec.recommendation_type.value
            if rec.recommendation_type
            else "Recommendation"
        ),
        recommendation=rec.recommendation,
        confidence_score=(
            float(rec.confidence_score) if rec.confidence_score is not None else None
        ),
        status=rec.decision_status.value,
        resolved_by=rec.resolved_by,
        resolved_at=rec.resolved_at,
        created_at=rec.created_at,
        metadata_json=rec.metadata_json,
    )


def _get_card(
    db: Session, card_id: uuid.UUID, current: CurrentUser
) -> AIRecommendation:
    rec = db.get(AIRecommendation, card_id, options=[lazyload("*")])
    if rec is None or rec.is_deleted or rec.workspace_id != current.workspace_id:
        raise AppError(404, "not_found", "Decision card not found")
    return rec


@router.get("", response_model=list[DecisionCardOut])
def list_cards(
    status: str | None = Query(None, pattern="^(pending|approved|rejected)$"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[DecisionCardOut]:
    stmt = (
        select(AIRecommendation)
        .where(
            AIRecommendation.workspace_id == current.workspace_id,
            AIRecommendation.is_deleted.is_(False),
        )
        .options(lazyload("*"))
    )
    if status is not None:
        stmt = stmt.where(AIRecommendation.decision_status == DecisionStatus(status))
    stmt = stmt.order_by(AIRecommendation.created_at.desc()).limit(limit).offset(offset)
    return [to_out(r, current.sector) for r in db.execute(stmt).scalars().all()]


def _resolve(
    card_id: uuid.UUID,
    new_status: DecisionStatus,
    current: CurrentUser,
    db: Session,
) -> DecisionCardOut:
    rec = _get_card(db, card_id, current)
    rec.decision_status = new_status
    rec.resolved_by = current.id
    rec.resolved_at = datetime.now(timezone.utc)
    db.commit()
    return to_out(rec, current.sector)


@router.post("/{card_id}/approve", response_model=DecisionCardOut)
def approve_card(
    card_id: uuid.UUID,
    current: CurrentUser = Depends(require_roles("admin", "manager")),
    db: Session = Depends(get_db),
) -> DecisionCardOut:
    return _resolve(card_id, DecisionStatus.APPROVED, current, db)


@router.post("/{card_id}/reject", response_model=DecisionCardOut)
def reject_card(
    card_id: uuid.UUID,
    current: CurrentUser = Depends(require_roles("admin", "manager")),
    db: Session = Depends(get_db),
) -> DecisionCardOut:
    return _resolve(card_id, DecisionStatus.REJECTED, current, db)


from pydantic import BaseModel  # noqa: E402


class DecisionGenerateRequest(BaseModel):
    query: str
    dataset_id: uuid.UUID | None = None


from app.services.decision_service import DecisionService  # noqa: E402


@router.post("/generate", response_model=DecisionCardOut)
def generate_decision_card(
    request: DecisionGenerateRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DecisionCardOut:
    """
    Triggers automated decision card generation based on search context.
    Calculates weights, runs validation, and saves metadata.
    """
    decision_svc = DecisionService(db)
    card = decision_svc.generate_decision_card(
        organization_id=current.organization_id,
        workspace_id=current.workspace_id,
        query=request.query,
        dataset_id=request.dataset_id,
    )
    db.commit()
    return to_out(card, current.sector)
