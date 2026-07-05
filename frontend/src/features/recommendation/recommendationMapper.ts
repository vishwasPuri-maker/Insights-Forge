import type { 
  RecommendationAnalysisDTO, 
  RecommendationAnalysis,
  ExecutiveRecommendationDTO,
  ExecutiveRecommendation,
  ActionPlanDTO,
  ActionPlan,
  ActionPlanStepDTO,
  ActionPlanStep,
  ROIProjectionDTO,
  ROIProjection,
  ApprovalWorkflowDTO,
  ApprovalWorkflow,
  ApprovalWorkflowStepDTO,
  ApprovalWorkflowStep
} from '@/types/recommendation';

export const mapActionPlanStep = (dto: ActionPlanStepDTO): ActionPlanStep => ({
  id: dto.id,
  description: dto.description,
  owner: dto.owner,
  estimatedDays: dto.estimated_days,
  dependencies: dto.dependencies
});

export const mapActionPlan = (dto: ActionPlanDTO): ActionPlan => ({
  id: dto.id,
  title: dto.title,
  totalEstimatedDays: dto.total_estimated_days,
  steps: dto.steps.map(mapActionPlanStep)
});

export const mapROIProjection = (dto: ROIProjectionDTO): ROIProjection => ({
  id: dto.id,
  projectedValue: dto.projected_value,
  paybackPeriodDays: dto.payback_period_days,
  confidenceLower: dto.confidence_lower,
  confidenceUpper: dto.confidence_upper
});

export const mapApprovalWorkflowStep = (dto: ApprovalWorkflowStepDTO): ApprovalWorkflowStep => ({
  id: dto.id,
  role: dto.role,
  status: dto.status
});

export const mapApprovalWorkflow = (dto: ApprovalWorkflowDTO): ApprovalWorkflow => ({
  id: dto.id,
  finalStatus: dto.final_status,
  steps: dto.steps.map(mapApprovalWorkflowStep)
});

export const mapExecutiveRecommendation = (dto: ExecutiveRecommendationDTO): ExecutiveRecommendation => ({
  id: dto.id,
  title: dto.title,
  description: dto.description,
  priority: dto.priority,
  impactScore: dto.impact_score,
  riskScore: dto.risk_score,
  roi: mapROIProjection(dto.roi),
  actionPlan: mapActionPlan(dto.action_plan),
  approval: mapApprovalWorkflow(dto.approval)
});

export const mapRecommendationAnalysis = (dto: RecommendationAnalysisDTO): RecommendationAnalysis => {
  return {
    id: dto.id,
    tenantId: dto.tenant_id,
    sectorId: dto.sector_id,
    metadata: {
      generatedAt: dto.metadata.generated_at,
      modelId: dto.metadata.model_id,
      processingTimeMs: dto.metadata.processing_time_ms
    },
    confidence: {
      actionabilityScore: dto.confidence.actionability_score,
      dataQualityScore: dto.confidence.data_quality_score,
      modelCertainty: dto.confidence.model_certainty
    },
    summary: {
      topic: dto.summary.topic,
      executiveSummary: dto.summary.executive_summary,
      primaryConclusion: dto.summary.primary_conclusion
    },
    recommendations: dto.recommendations.map(mapExecutiveRecommendation)
  };
};
