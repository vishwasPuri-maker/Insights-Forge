"""Record schemas — frozen by contract (RecordOut, RecordsPage)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


class RecordOut(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    sector: str
    data: dict
    recorded_at: datetime | None = None
    created_at: datetime


class RecordsPage(BaseModel):
    sector: str
    total: int
    limit: int
    offset: int
    items: list[RecordOut]
