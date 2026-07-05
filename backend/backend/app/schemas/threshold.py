"""Threshold schemas — frozen by contract (ThresholdOut, ThresholdUpdate)."""

from __future__ import annotations

import uuid

from pydantic import BaseModel


class ThresholdOut(BaseModel):
    id: uuid.UUID
    sector: str
    metric_key: str
    label: str
    warning_value: float | None = None
    critical_value: float | None = None


class ThresholdUpdate(BaseModel):
    warning_value: float | None = None
    critical_value: float | None = None
