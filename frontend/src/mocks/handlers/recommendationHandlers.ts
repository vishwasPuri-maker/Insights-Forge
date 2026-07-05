import { http, HttpResponse } from 'msw';
import type { RecommendationAnalysisDTO } from '@/types/recommendation';

const mockRecommendationDTO: RecommendationAnalysisDTO = {
  id: 'rec_001',
  tenant_id: 't1',
  sector_id: 's1',
  summary: {
    topic: 'Strategic Market Entry',
    executive_summary: 'Proceed with market entry based on high ROI and manageable risks.',
    primary_conclusion: 'Strongly Recommended'
  },
  confidence: {
    actionability_score: 0.95,
    data_quality_score: 0.88,
    model_certainty: 0.92
  },
  metadata: {
    generated_at: new Date().toISOString(),
    model_id: 'decision-v1',
    processing_time_ms: 1240
  },
  recommendations: [
    {
      id: 'rec_item_1',
      title: 'Acquire Primary Competitor',
      description: 'Acquiring the target will increase market share by 15% immediately.',
      priority: 'high',
      impact_score: 0.85,
      risk_score: 0.40,
      roi: {
        id: 'roi_1',
        projected_value: 2500000,
        payback_period_days: 180,
        confidence_lower: 2000000,
        confidence_upper: 3000000
      },
      action_plan: {
        id: 'ap_1',
        title: 'Acquisition Strategy',
        total_estimated_days: 120,
        steps: [
          {
            id: 'step_1',
            description: 'Due Diligence',
            owner: 'Legal Team',
            estimated_days: 30,
            dependencies: []
          }
        ]
      },
      approval: {
        id: 'app_1',
        final_status: 'pending',
        steps: [
          {
            id: 'app_step_1',
            role: 'CFO',
            status: 'required'
          },
          {
            id: 'app_step_2',
            role: 'CEO',
            status: 'required'
          }
        ]
      }
    }
  ]
};

export const recommendationHandlers = [
  http.get('/api/v1/tenants/:tenantId/sectors/:sectorId/recommendation', ({ params }) => {
    const { tenantId, sectorId } = params;
    
    // Simulate tenant isolation enforcement at API level
    if (tenantId !== 't1') {
      return new HttpResponse(null, { status: 403, statusText: 'Forbidden' });
    }

    // Clone and inject specific identifiers to prove correct routing
    const response = {
      ...mockRecommendationDTO,
      tenant_id: tenantId as string,
      sector_id: sectorId as string,
    };

    return HttpResponse.json(response);
  })
];
