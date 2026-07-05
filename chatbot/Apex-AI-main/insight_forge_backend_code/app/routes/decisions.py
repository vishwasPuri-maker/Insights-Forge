"""Decision-card routes: list, approve, reject.

Cards are AI-recommended actions produced elsewhere; this backend serves them and
records the manager's decision. Reading is open to any authenticated role;
approve/reject requires `manager` or `admin` (RBAC). Every query is org-scoped
under RLS and filtered by organization_id explicitly.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.jwt_handler import TokenData, get_current_user, require_role
from app.database import get_db, set_organization_context
from app.models import DecisionCard
from app.schemas import DecisionCardOut

router = APIRouter(prefix="/decision-cards", tags=["decision-cards"])


@router.get("", response_model=list[DecisionCardOut])
def list_decision_cards(
    current: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db),
    status_filter: str | None = Query(
        None, alias="status", pattern="^(pending|approved|rejected)$"
    ),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> list[DecisionCard]:
    set_organization_context(db, current.organization_id)
    stmt = (
        select(DecisionCard)
        .where(
            DecisionCard.organization_id == uuid.UUID(current.organization_id),
            DecisionCard.sector == current.sector,
        )
        .order_by(DecisionCard.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if status_filter is not None:
        stmt = stmt.where(DecisionCard.status == status_filter)
    return list(db.scalars(stmt).all())


def _decide(db: Session, current: TokenData, card_id: uuid.UUID, new_status: str) -> DecisionCard:
    set_organization_context(db, current.organization_id)
    card = db.scalar(
        select(DecisionCard).where(
            DecisionCard.id == card_id,
            DecisionCard.organization_id == uuid.UUID(current.organization_id),
            DecisionCard.sector == current.sector,
        )
    )
    if card is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "decision card not found"},
        )
    if card.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "already_decided", "message": f"card already {card.status}"},
        )
    card.status = new_status
    card.resolved_by = uuid.UUID(current.user_id)
    card.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(card)
    return card


@router.post("/{card_id}/approve", response_model=DecisionCardOut)
def approve(
    card_id: uuid.UUID,
    current: TokenData = Depends(require_role("manager", "admin")),
    db: Session = Depends(get_db),
) -> DecisionCard:
    return _decide(db, current, card_id, "approved")


@router.post("/{card_id}/reject", response_model=DecisionCardOut)
def reject(
    card_id: uuid.UUID,
    current: TokenData = Depends(require_role("manager", "admin")),
    db: Session = Depends(get_db),
) -> DecisionCard:
    return _decide(db, current, card_id, "rejected")
