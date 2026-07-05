import type {
  ReasoningAnalysis,
  ReasoningAnalysisDTO,
  ReasoningInsight,
  ReasoningInsightDTO,
  ReasoningFactor,
  ReasoningFactorDTO,
  ReasoningEvidence,
  ReasoningEvidenceDTO,
  ReasoningEdge,
  ReasoningEdgeDTO,
  ReasoningRecommendation,
  ReasoningRecommendationDTO,
  ReasoningConfidence,
  ReasoningConfidenceDTO,
  ReasoningSummary,
  ReasoningSummaryDTO,
  ReasoningMetadata,
  ReasoningMetadataDTO,
} from '@/types/reasoning';

export const mapReasoningSummary = (dto: ReasoningSummaryDTO): ReasoningSummary => ({
  topic: dto.topic,
  executiveSummary: dto.executive_summary,
  primaryConclusion: dto.primary_conclusion,
});

export const mapReasoningInsight = (dto: ReasoningInsightDTO): ReasoningInsight => ({
  id: dto.id,
  title: dto.title,
  description: dto.description,
  severity: dto.severity,
  category: dto.category,
});

export const mapReasoningFactor = (dto: ReasoningFactorDTO): ReasoningFactor => ({
  id: dto.id,
  name: dto.name,
  contributionWeight: dto.contribution_weight,
  trend: dto.trend,
});

export const mapReasoningEvidence = (dto: ReasoningEvidenceDTO): ReasoningEvidence => ({
  id: dto.id,
  source: dto.source,
  description: dto.description,
  reliability: dto.reliability,
});

export const mapReasoningEdge = (dto: ReasoningEdgeDTO): ReasoningEdge => ({
  id: dto.id,
  sourceId: dto.source_id,
  targetId: dto.target_id,
  relationship: dto.relationship,
  strength: dto.strength,
});

export const mapReasoningRecommendation = (dto: ReasoningRecommendationDTO): ReasoningRecommendation => ({
  id: dto.id,
  title: dto.title,
  description: dto.description,
  impactScore: dto.impact_score,
  effortLevel: dto.effort_level,
  actionType: dto.action_type,
});

export const mapReasoningConfidence = (dto: ReasoningConfidenceDTO): ReasoningConfidence => ({
  overallScore: dto.overall_score,
  dataQualityScore: dto.data_quality_score,
  modelCertainty: dto.model_certainty,
});

export const mapReasoningMetadata = (dto: ReasoningMetadataDTO): ReasoningMetadata => ({
  generatedAt: dto.generated_at,
  modelId: dto.model_id,
  processingTimeMs: dto.processing_time_ms,
});

export const mapReasoningAnalysis = (dto: ReasoningAnalysisDTO): ReasoningAnalysis => ({
  id: dto.id,
  tenantId: dto.tenant_id,
  sectorId: dto.sector_id,
  summary: mapReasoningSummary(dto.summary),
  insights: dto.insights.map(mapReasoningInsight),
  factors: dto.factors.map(mapReasoningFactor),
  evidenceNodes: dto.evidence_nodes.map(mapReasoningEvidence),
  evidenceEdges: dto.evidence_edges.map(mapReasoningEdge),
  recommendations: dto.recommendations.map(mapReasoningRecommendation),
  confidence: mapReasoningConfidence(dto.confidence),
  metadata: mapReasoningMetadata(dto.metadata),
});
