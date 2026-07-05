"""Ingestion schemas — frozen by contract (IngestionResponse)."""

from __future__ import annotations

from pydantic import BaseModel


class IngestionResponse(BaseModel):
    dataset_id: str
    sector: str
    status: str
    size_bytes: int | None = None
    message: str | None = None
