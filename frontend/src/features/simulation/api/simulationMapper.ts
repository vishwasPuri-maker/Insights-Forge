import type { SimulationAnalysis, SimulationAnalysisDTO, SimulationScenario, SimulationScenarioDTO } from '@/types/simulation';

const mapScenario = (dto: SimulationScenarioDTO): SimulationScenario => ({
  id: dto.id,
  name: dto.name,
  status: dto.status,
  parameters: dto.parameters.map(p => ({
    id: p.id,
    name: p.name,
    currentValue: p.current_value,
    proposedValue: p.proposed_value,
    bounds: p.bounds,
    unit: p.unit
  })),
  forecasts: dto.forecasts.map(f => ({
    id: f.id,
    metric: f.metric,
    predictedValue: f.predicted_value,
    confidenceLower: f.confidence_lower,
    confidenceUpper: f.confidence_upper,
    targetDate: f.target_date
  })),
  outcomes: dto.outcomes.map(o => ({
    id: o.id,
    title: o.title,
    description: o.description,
    impactScore: o.impact_score,
    probability: o.probability
  })),
  risks: dto.risks.map(r => ({
    id: r.id,
    description: r.description,
    severity: r.severity,
    mitigationStrategy: r.mitigation_strategy
  }))
});

export const mapSimulationAnalysis = (dto: SimulationAnalysisDTO): SimulationAnalysis => ({
  id: dto.id,
  tenantId: dto.tenant_id,
  sectorId: dto.sector_id,
  summary: {
    topic: dto.summary.topic,
    executiveSummary: dto.summary.executive_summary,
    primaryConclusion: dto.summary.primary_conclusion
  },
  baselineScenario: mapScenario(dto.baseline_scenario),
  proposedScenario: mapScenario(dto.proposed_scenario),
  recommendations: dto.recommendations.map(r => ({
    id: r.id,
    title: r.title,
    description: r.description,
    impactScore: r.impact_score,
    effortLevel: r.effort_level,
    actionType: r.action_type
  })),
  confidence: {
    overallScore: dto.confidence.overall_score,
    dataQualityScore: dto.confidence.data_quality_score,
    modelCertainty: dto.confidence.model_certainty
  },
  metadata: {
    generatedAt: dto.metadata.generated_at,
    modelId: dto.metadata.model_id,
    processingTimeMs: dto.metadata.processing_time_ms
  }
});
