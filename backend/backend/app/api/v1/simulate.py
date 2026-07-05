"""Simulation endpoint — deterministic what-if projection over metrics."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, get_current_user
from app.db.session import get_db
from app.schemas.simulate import (
    SimulateProjection,
    SimulateRequest,
    SimulateResponse,
)

router = APIRouter(prefix="/simulate", tags=["Simulate"])


@router.post("", response_model=SimulateResponse)
def simulate(
    payload: SimulateRequest,
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SimulateResponse:
    projections: list[SimulateProjection] = []
    total_current = 0.0
    total_projected = 0.0
    for metric in payload.metrics:
        projected = metric.current * (1 + metric.change_pct / 100.0)
        total_current += metric.current
        total_projected += projected
        projections.append(
            SimulateProjection(
                key=metric.key,
                current=metric.current,
                projected=round(projected, 4),
                change_pct=metric.change_pct,
            )
        )
    return SimulateResponse(
        sector=current.sector,
        projections=projections,
        total_current=round(total_current, 4),
        total_projected=round(total_projected, 4),
    )
