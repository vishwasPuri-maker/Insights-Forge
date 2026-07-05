import { describe, it, expect } from 'vitest';
import { mapRecommendationAnalysis } from '../recommendationMapper';
import type { RecommendationAnalysisDTO } from '@/types/recommendation';

describe('recommendationMapper', () => {
  const mockDTO: RecommendationAnalysisDTO = {
    id: 'rec_001',
    tenant_id: 'tenant-a',
    sector_id: 'sector-b',
    summary: {
      topic: 'Topic',
      executive_summary: 'Summary',
      primary_conclusion: 'Conclusion'
    },
    confidence: {
      actionability_score: 0.9,
      data_quality_score: 0.8,
      model_certainty: 0.85
    },
    metadata: {
      generated_at: '2025-01-01',
      model_id: 'm1',
      processing_time_ms: 100
    },
    recommendations: [
      {
        id: 'r1',
        title: 'Title',
        description: 'Desc',
        priority: 'high',
        impact_score: 0.9,
        risk_score: 0.2,
        roi: {
          id: 'roi1',
          projected_value: 100,
          payback_period_days: 30,
          confidence_lower: 90,
          confidence_upper: 110
        },
        action_plan: {
          id: 'ap1',
          title: 'AP Title',
          total_estimated_days: 10,
          steps: [
            {
              id: 's1',
              description: 'Step',
              owner: 'Me',
              estimated_days: 10,
              dependencies: []
            }
          ]
        },
        approval: {
          id: 'app1',
          final_status: 'pending',
          steps: [
            {
              id: 'as1',
              role: 'CFO',
              status: 'required'
            }
          ]
        }
      }
    ]
  };

  it('maps DTO to Domain perfectly', () => {
    const domain = mapRecommendationAnalysis(mockDTO);
    expect(domain.id).toBe('rec_001');
    expect(domain.tenantId).toBe('tenant-a');
    expect(domain.sectorId).toBe('sector-b');
    expect(domain.metadata.processingTimeMs).toBe(100);
    expect(domain.confidence.actionabilityScore).toBe(0.9);
    
    const rec = domain.recommendations[0];
    expect(rec.impactScore).toBe(0.9);
    expect(rec.roi.projectedValue).toBe(100);
    expect(rec.actionPlan.totalEstimatedDays).toBe(10);
    expect(rec.actionPlan.steps[0].estimatedDays).toBe(10);
    expect(rec.approval.finalStatus).toBe('pending');
  });
});
