# /scraper/validation_schema.py
# Task 2: Resilient Market Intelligence Spider & Validation Barrier
# Mapping: Doc 2 (TRD Section 9.3), Doc 1 (PRD Section 1.1)
"""
Pydantic structural data-type integrity matrix used to score every scraped
row before it is allowed to land in the S3 raw bucket. Rows scoring below
0.70 structural completeness are routed to an append-only dead-letter path.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

DEAD_LETTER_THRESHOLD = 0.70

REQUIRED_FIELDS = [
    "tenant_id",
    "source_url",
    "indicator_name",
    "indicator_metric",
    "temporal_stamp",
]


class InboundTelemetryModel(BaseModel):
    """Structural contract for a single scraped market-intelligence record."""

    tenant_id: uuid.UUID
    source_url: str
    indicator_name: str
    indicator_metric: float = Field(..., ge=0.0, le=1.0)
    temporal_stamp: str
    sector: Optional[str] = None
    raw_snippet: Optional[str] = None

    @field_validator("indicator_metric")
    @classmethod
    def verify_range(cls, value: float) -> float:
        if not (0.0 <= value <= 1.0):
            raise ValueError("Telemetry out of logical bounds")
        return value

    @field_validator("temporal_stamp")
    @classmethod
    def verify_parseable(cls, value: str) -> str:
        # Accept any commonly-scraped date format; normalization to ISO 8601
        # happens downstream in the PySpark sanitization stage.
        if not value or len(value) < 6:
            raise ValueError("temporal_stamp is missing or malformed")
        return value


def score_structural_completeness(raw_row: dict) -> float:
    """Fraction of REQUIRED_FIELDS present and non-null in a raw scraped dict."""
    present = sum(
        1
        for field in REQUIRED_FIELDS
        if raw_row.get(field) not in (None, "", "null")
    )
    return round(present / len(REQUIRED_FIELDS), 4)


def validate_row(raw_row: dict) -> tuple[bool, Optional[InboundTelemetryModel], float]:
    """
    Validate a single scraped row.

    Returns (is_valid, parsed_model_or_None, completeness_score).
    Rows with completeness_score < DEAD_LETTER_THRESHOLD are always rejected,
    even if they happen to parse, and must be written to the dead-letter archive.
    """
    score = score_structural_completeness(raw_row)
    if score < DEAD_LETTER_THRESHOLD:
        return False, None, score

    try:
        model = InboundTelemetryModel(**raw_row)
        return True, model, score
    except Exception:
        return False, None, score
