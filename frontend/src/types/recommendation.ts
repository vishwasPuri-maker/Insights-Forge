/**
 * DOMAIN MODELS (UI Consumption Only - strictly camelCase)
 */

export interface RecommendationMetadata {
  generatedAt: string;
  modelId: string;
  processingTimeMs: number;
}

export interface RecommendationConfidence {
  actionabilityScore: number; // 0.0 - 1.0
  dataQualityScore: number; // 0.0 - 1.0
  modelCertainty: number; // 0.0 - 1.0
}

export interface RecommendationSummary {
  topic: string;
  executiveSummary: string;
  primaryConclusion: string;
}

export interface ActionPlanStep {
  id: string;
  description: string;
  owner: string;
  estimatedDays: number;
  dependencies: string[]; // Step IDs
}

export interface ActionPlan {
  id: string;
  title: string;
  steps: ActionPlanStep[];
  totalEstimatedDays: number;
}

export interface ROIProjection {
  id: string;
  projectedValue: number;
  paybackPeriodDays: number;
  confidenceLower: number;
  confidenceUpper: number;
}

export interface ApprovalWorkflowStep {
  id: string;
  role: string; // e.g. "CFO", "VP Engineering"
  status: 'pending' | 'approved' | 'rejected' | 'required';
}

export interface ApprovalWorkflow {
  id: string;
  steps: ApprovalWorkflowStep[];
  finalStatus: 'pending' | 'approved' | 'rejected';
}

export interface ExecutiveRecommendation {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  impactScore: number; // 0.0 - 1.0
  riskScore: number; // 0.0 - 1.0
  roi: ROIProjection;
  actionPlan: ActionPlan;
  approval: ApprovalWorkflow;
}

export interface RecommendationAnalysis {
  id: string;
  tenantId: string;
  sectorId: string;
  summary: RecommendationSummary;
  recommendations: ExecutiveRecommendation[];
  confidence: RecommendationConfidence;
  metadata: RecommendationMetadata;
}

/**
 * DTO MODELS (Backend Payload Exact Match - strictly snake_case)
 */

export interface RecommendationMetadataDTO {
  generated_at: string;
  model_id: string;
  processing_time_ms: number;
}

export interface RecommendationConfidenceDTO {
  actionability_score: number;
  data_quality_score: number;
  model_certainty: number;
}

export interface RecommendationSummaryDTO {
  topic: string;
  executive_summary: string;
  primary_conclusion: string;
}

export interface ActionPlanStepDTO {
  id: string;
  description: string;
  owner: string;
  estimated_days: number;
  dependencies: string[];
}

export interface ActionPlanDTO {
  id: string;
  title: string;
  steps: ActionPlanStepDTO[];
  total_estimated_days: number;
}

export interface ROIProjectionDTO {
  id: string;
  projected_value: number;
  payback_period_days: number;
  confidence_lower: number;
  confidence_upper: number;
}

export interface ApprovalWorkflowStepDTO {
  id: string;
  role: string;
  status: 'pending' | 'approved' | 'rejected' | 'required';
}

export interface ApprovalWorkflowDTO {
  id: string;
  steps: ApprovalWorkflowStepDTO[];
  final_status: 'pending' | 'approved' | 'rejected';
}

export interface ExecutiveRecommendationDTO {
  id: string;
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  impact_score: number;
  risk_score: number;
  roi: ROIProjectionDTO;
  action_plan: ActionPlanDTO;
  approval: ApprovalWorkflowDTO;
}

export interface RecommendationAnalysisDTO {
  id: string;
  tenant_id: string;
  sector_id: string;
  summary: RecommendationSummaryDTO;
  recommendations: ExecutiveRecommendationDTO[];
  confidence: RecommendationConfidenceDTO;
  metadata: RecommendationMetadataDTO;
}
