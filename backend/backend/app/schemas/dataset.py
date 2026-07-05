"""Dataset schemas — frozen by contract_reference.json (DatasetOut)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class DatasetOut(BaseModel):
    id: uuid.UUID
    sector: str
    original_filename: str
    status: str
    health_score: float | None = None
    size_bytes: int | None = None
    content_type: str | None = None
    uploaded_by: uuid.UUID
    created_at: datetime
    total_rows: int | None = None
    description: str | None = None
