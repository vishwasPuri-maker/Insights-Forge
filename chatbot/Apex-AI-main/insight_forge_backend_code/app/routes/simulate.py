"""What-if simulator: POST /simulate.

Takes a set of metrics with their current values and a percentage change, and
returns the recalculated projections **in memory**. It never writes to any table
— purely a deterministic arithmetic projection (projected = current * (1 + pct/100)).
This is not ML/forecasting; just a scenario calculator for the dashboard.
"""
from fastapi import APIRouter, Depends

from app.auth.jwt_handler import TokenData, get_current_user
from app.schemas import SimulateProjection, SimulateRequest, SimulateResponse

router = APIRouter(tags=["simulate"])


@router.post("/simulate", response_model=SimulateResponse)
def simulate(
    body: SimulateRequest,
    current: TokenData = Depends(get_current_user),
) -> SimulateResponse:
    projections: list[SimulateProjection] = []
    total_current = 0.0
    total_projected = 0.0
    for m in body.metrics:
        projected = round(m.current * (1 + m.change_pct / 100.0), 4)
        total_current += m.current
        total_projected += projected
        projections.append(
            SimulateProjection(
                key=m.key, current=m.current, projected=projected, change_pct=m.change_pct
            )
        )
    return SimulateResponse(
        sector=current.sector,
        projections=projections,
        total_current=round(total_current, 4),
        total_projected=round(total_projected, 4),
    )
