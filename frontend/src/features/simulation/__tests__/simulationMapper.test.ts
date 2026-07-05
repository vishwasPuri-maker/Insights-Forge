import { describe, it, expect } from 'vitest';
import { mapSimulationAnalysis } from '../api/simulationMapper';
import type { SimulationAnalysisDTO } from '@/types/simulation';

describe('simulationMapper', () => {
  it('maps DTO to Domain model correctly', () => {
    const dto: SimulationAnalysisDTO = {
      id: '1',
      tenant_id: 't1',
      sector_id: 's1',
      summary: {
        topic: 'topic',
        executive_summary: 'exec',
        primary_conclusion: 'conc'
      },
      baseline_scenario: {
        id: 'bs', name: 'base', status: 'completed',
        parameters: [{ id: 'p1', name: 'p1', current_value: 10, proposed_value: 10, bounds: [0, 20], unit: 'x' }],
        forecasts: [{ id: 'f1', metric: 'm', predicted_value: 100, confidence_lower: 90, confidence_upper: 110, target_date: '2026' }],
        outcomes: [{ id: 'o1', title: 'o1', description: 'd', impact_score: 0.5, probability: 0.5 }],
        risks: [{ id: 'r1', description: 'r', severity: 'low', mitigation_strategy: 'm' }]
      },
      proposed_scenario: {
        id: 'ps', name: 'prop', status: 'completed', parameters: [], forecasts: [], outcomes: [], risks: []
      },
      recommendations: [{ id: 'rec', title: 't', description: 'd', impact_score: 0.8, effort_level: 'low', action_type: 'optimize' }],
      confidence: { overall_score: 0.9, data_quality_score: 0.9, model_certainty: 0.9 },
      metadata: { generated_at: 'date', model_id: 'm1', processing_time_ms: 100 }
    };

    const domain = mapSimulationAnalysis(dto);
    
    expect(domain.id).toBe('1');
    expect(domain.summary.executiveSummary).toBe('exec');
    expect(domain.baselineScenario.parameters[0].currentValue).toBe(10);
    expect(domain.baselineScenario.forecasts[0].confidenceLower).toBe(90);
    expect(domain.baselineScenario.outcomes[0].impactScore).toBe(0.5);
    expect(domain.baselineScenario.risks[0].mitigationStrategy).toBe('m');
    expect(domain.recommendations[0].effortLevel).toBe('low');
    expect(domain.confidence.overallScore).toBe(0.9);
    expect(domain.metadata.processingTimeMs).toBe(100);
  });
});
