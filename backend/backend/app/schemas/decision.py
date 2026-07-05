"""
Decision-card schemas — frozen by contract (DecisionCardOut) with dynamic Pydantic support.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.enums import AIRecommendationPriority, AIRecommendationType


class DecisionKPI(BaseModel):
    metric: str
    value: str
    target: str | None = None

    model_config = ConfigDict(from_attributes=True)


class DecisionSource(BaseModel):
    document_id: str
    chunk_id: str
    page: int | None = None
    score: float | None = None

    model_config = ConfigDict(from_attributes=True)


class DecisionExplanation(BaseModel):
    reasoning: str
    evidence: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    confidence_reason: str
    limitations: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class DecisionOutput(BaseModel):
    title: str
    summary: str
    recommendation: str
    confidence: float
    priority: AIRecommendationPriority
    recommendation_type: AIRecommendationType
    explanation: DecisionExplanation
    kpis: list[DecisionKPI] = Field(default_factory=list)
    sources: list[DecisionSource] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    generated_at: datetime
    model_used: str
    retrieval_score: float
    retrieved_documents_count: int
    provider: str
    embedding_model: str
    prompt_version: str
    version: str = "1.0.0"

    model_config = ConfigDict(from_attributes=True)


class DecisionCardOut(BaseModel):
    id: uuid.UUID
    sector: str
    title: str
    recommendation: str | None = None
    confidence_score: float | None = None
    status: str
    resolved_by: uuid.UUID | None = None
    resolved_at: datetime | None = None
    created_at: datetime
    metadata_json: dict | None = None

    model_config = ConfigDict(from_attributes=True)
