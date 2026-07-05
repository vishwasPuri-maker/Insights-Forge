"""Report schemas — frozen by contract (ReportCompileRequest, ReportOut)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ReportCompileRequest(BaseModel):
    report_type: str = Field(min_length=1, max_length=64)
    params: dict | None = None


class ReportOut(BaseModel):
    id: uuid.UUID
    sector: str
    report_type: str
    status: str
    download_url: str | None = None
    created_at: datetime
