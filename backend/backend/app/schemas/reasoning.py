from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel


class ReasoningMetadataDTO(BaseModel):
    generated_at: str
    model_id: str
    processing_time_ms: int


class ReasoningConfidenceDTO(BaseModel):
    overall_score: float
    data_quality_score: float
    model_certainty: float


class ReasoningRecommendationDTO(BaseModel):
    id: str
    title: str
    description: str
    impact_score: float
    effort_level: Literal["low", "medium", "high"]
    action_type: Literal["optimize", "investigate", "mitigate", "escalate"]


class ReasoningEdgeDTO(BaseModel):
    id: str
    source_id: str
    target_id: str
    relationship: Literal["causes", "supports", "contradicts", "correlates"]
    strength: float


class ReasoningEvidenceDTO(BaseModel):
    id: str
    source: str
    description: str
    reliability: float


class ReasoningFactorDTO(BaseModel):
    id: str
    name: str
    contribution_weight: float
    trend: Literal["increasing", "stable", "decreasing"]


class ReasoningInsightDTO(BaseModel):
    id: str
    title: str
    description: str
    severity: Literal["low", "medium", "high", "critical"]
    category: Literal["anomaly", "trend", "forecast", "system"]


class ReasoningSummaryDTO(BaseModel):
    topic: str
    executive_summary: str
    primary_conclusion: str


class ReasoningAnalysisDTO(BaseModel):
    id: str
    tenant_id: str
    sector_id: str
    summary: ReasoningSummaryDTO
    insights: List[ReasoningInsightDTO]
    factors: List[ReasoningFactorDTO]
    evidence_nodes: List[ReasoningEvidenceDTO]
    evidence_edges: List[ReasoningEdgeDTO]
    recommendations: List[ReasoningRecommendationDTO]
    confidence: ReasoningConfidenceDTO
    metadata: ReasoningMetadataDTO
