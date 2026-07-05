/**
 * DOMAIN MODELS (UI Consumption Only - strictly camelCase)
 */

export interface SimulationMetadata {
  generatedAt: string;
  modelId: string;
  processingTimeMs: number;
}

export interface SimulationConfidence {
  overallScore: number;
  dataQualityScore: number;
  modelCertainty: number;
}

export interface SimulationSummary {
  topic: string;
  executiveSummary: string;
  primaryConclusion: string;
}

export interface SimulationParameter {
  id: string;
  name: string;
  currentValue: number;
  proposedValue: number;
  bounds: [number, number];
  unit: string;
}

export interface SimulationForecast {
  id: string;
  metric: string;
  predictedValue: number;
  confidenceLower: number;
  confidenceUpper: number;
  targetDate: string;
}

export interface SimulationOutcome {
  id: string;
  title: string;
  description: string;
  impactScore: number; // 0.0 - 1.0
  probability: number; // 0.0 - 1.0
}

export interface SimulationRisk {
  id: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  mitigationStrategy: string;
}

export interface SimulationRecommendation {
  id: string;
  title: string;
  description: string;
  impactScore: number;
  effortLevel: 'low' | 'medium' | 'high';
  actionType: 'optimize' | 'investigate' | 'mitigate' | 'escalate';
}

export interface SimulationScenario {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  parameters: SimulationParameter[];
  forecasts: SimulationForecast[];
  outcomes: SimulationOutcome[];
  risks: SimulationRisk[];
}

export interface SimulationAnalysis {
  id: string;
  tenantId: string;
  sectorId: string;
  summary: SimulationSummary;
  baselineScenario: SimulationScenario;
  proposedScenario: SimulationScenario;
  recommendations: SimulationRecommendation[];
  confidence: SimulationConfidence;
  metadata: SimulationMetadata;
}

/**
 * DTO MODELS (Backend Payload Exact Match - strictly snake_case)
 */

export interface SimulationMetadataDTO {
  generated_at: string;
  model_id: string;
  processing_time_ms: number;
}

export interface SimulationConfidenceDTO {
  overall_score: number;
  data_quality_score: number;
  model_certainty: number;
}

export interface SimulationSummaryDTO {
  topic: string;
  executive_summary: string;
  primary_conclusion: string;
}

export interface SimulationParameterDTO {
  id: string;
  name: string;
  current_value: number;
  proposed_value: number;
  bounds: [number, number];
  unit: string;
}

export interface SimulationForecastDTO {
  id: string;
  metric: string;
  predicted_value: number;
  confidence_lower: number;
  confidence_upper: number;
  target_date: string;
}

export interface SimulationOutcomeDTO {
  id: string;
  title: string;
  description: string;
  impact_score: number;
  probability: number;
}

export interface SimulationRiskDTO {
  id: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  mitigation_strategy: string;
}

export interface SimulationRecommendationDTO {
  id: string;
  title: string;
  description: string;
  impact_score: number;
  effort_level: 'low' | 'medium' | 'high';
  action_type: 'optimize' | 'investigate' | 'mitigate' | 'escalate';
}

export interface SimulationScenarioDTO {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  parameters: SimulationParameterDTO[];
  forecasts: SimulationForecastDTO[];
  outcomes: SimulationOutcomeDTO[];
  risks: SimulationRiskDTO[];
}

export interface SimulationAnalysisDTO {
  id: string;
  tenant_id: string;
  sector_id: string;
  summary: SimulationSummaryDTO;
  baseline_scenario: SimulationScenarioDTO;
  proposed_scenario: SimulationScenarioDTO;
  recommendations: SimulationRecommendationDTO[];
  confidence: SimulationConfidenceDTO;
  metadata: SimulationMetadataDTO;
}
