/**
 * DOMAIN MODELS (UI Consumption Only)
 */

export interface ReasoningMetadata {
  generatedAt: string;
  modelId: string;
  processingTimeMs: number;
}

export interface ReasoningConfidence {
  overallScore: number; // 0.0 to 1.0
  dataQualityScore: number; // 0.0 to 1.0
  modelCertainty: number; // 0.0 to 1.0
}

export interface ReasoningRecommendation {
  id: string;
  title: string;
  description: string;
  impactScore: number; // 0.0 to 1.0
  effortLevel: 'low' | 'medium' | 'high';
  actionType: 'optimize' | 'investigate' | 'mitigate' | 'escalate';
}

export interface ReasoningEdge {
  id: string;
  sourceId: string;
  targetId: string;
  relationship: 'causes' | 'supports' | 'contradicts' | 'correlates';
  strength: number; // 0.0 to 1.0
}

export interface ReasoningEvidence {
  id: string;
  source: string;
  description: string;
  reliability: number; // 0.0 to 1.0
}

export interface ReasoningFactor {
  id: string;
  name: string;
  contributionWeight: number; // 0.0 to 1.0
  trend: 'increasing' | 'stable' | 'decreasing';
}

export interface ReasoningInsight {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'anomaly' | 'trend' | 'forecast' | 'system';
}

export interface ReasoningSummary {
  topic: string;
  executiveSummary: string;
  primaryConclusion: string;
}

export interface ReasoningAnalysis {
  id: string;
  tenantId: string;
  sectorId: string;
  summary: ReasoningSummary;
  insights: ReasoningInsight[];
  factors: ReasoningFactor[];
  evidenceNodes: ReasoningEvidence[];
  evidenceEdges: ReasoningEdge[];
  recommendations: ReasoningRecommendation[];
  confidence: ReasoningConfidence;
  metadata: ReasoningMetadata;
}

/**
 * DTO MODELS (Backend Payload Exact Match)
 */

export interface ReasoningMetadataDTO {
  generated_at: string;
  model_id: string;
  processing_time_ms: number;
}

export interface ReasoningConfidenceDTO {
  overall_score: number;
  data_quality_score: number;
  model_certainty: number;
}

export interface ReasoningRecommendationDTO {
  id: string;
  title: string;
  description: string;
  impact_score: number;
  effort_level: 'low' | 'medium' | 'high';
  action_type: 'optimize' | 'investigate' | 'mitigate' | 'escalate';
}

export interface ReasoningEdgeDTO {
  id: string;
  source_id: string;
  target_id: string;
  relationship: 'causes' | 'supports' | 'contradicts' | 'correlates';
  strength: number;
}

export interface ReasoningEvidenceDTO {
  id: string;
  source: string;
  description: string;
  reliability: number;
}

export interface ReasoningFactorDTO {
  id: string;
  name: string;
  contribution_weight: number;
  trend: 'increasing' | 'stable' | 'decreasing';
}

export interface ReasoningInsightDTO {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'anomaly' | 'trend' | 'forecast' | 'system';
}

export interface ReasoningSummaryDTO {
  topic: string;
  executive_summary: string;
  primary_conclusion: string;
}

export interface ReasoningAnalysisDTO {
  id: string;
  tenant_id: string;
  sector_id: string;
  summary: ReasoningSummaryDTO;
  insights: ReasoningInsightDTO[];
  factors: ReasoningFactorDTO[];
  evidence_nodes: ReasoningEvidenceDTO[];
  evidence_edges: ReasoningEdgeDTO[];
  recommendations: ReasoningRecommendationDTO[];
  confidence: ReasoningConfidenceDTO;
  metadata: ReasoningMetadataDTO;
}
