"""Simulation schemas — frozen by contract (Simulate*)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SimulateMetric(BaseModel):
    key: str = Field(min_length=1, max_length=64)
    current: float
    change_pct: float = 0.0


class SimulateProjection(BaseModel):
    key: str
    current: float
    projected: float
    change_pct: float


class SimulateRequest(BaseModel):
    metrics: list[SimulateMetric] = Field(min_length=1)


class SimulateResponse(BaseModel):
    sector: str
    projections: list[SimulateProjection]
    total_current: float
    total_projected: float
