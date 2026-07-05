import { describe, it, expect } from 'vitest';
import { mapDashboardSummary } from '../api/dashboardMapper';
import type { DashboardSummaryDTO } from '@/types/dashboard';

describe('dashboardMapper', () => {
  it('correctly maps DashboardSummaryDTO to Domain Model', () => {
    const dto: DashboardSummaryDTO = {
      tenant_id: 't-1',
      sector_id: 's-1',
      last_updated: '2026-07-01T00:00:00Z',
      kpis: [
        {
          id: 'k1',
          title: 'Revenue',
          value: 1000,
          unit: '$',
          trend: { value: 5, direction: 'up', label: 'vs last month' }
        }
      ],
      forecasts: [
        {
          id: 'f1',
          metric: 'Revenue',
          predicted_value: 1200,
          confidence_lower: 1100,
          confidence_upper: 1300,
          target_date: '2026-08-01'
        }
      ],
      anomalies: [
        {
          id: 'a1',
          metric: 'Orders',
          deviation_score: 4.5,
          severity: 'high',
          detected_at: '2026-07-01T08:00:00Z',
          description: 'Spike in orders'
        }
      ],
      recommendations: [
        {
          id: 'r1',
          title: 'Scale Servers',
          description: 'Increase capacity',
          impact_score: 95,
          effort_level: 'low',
          action_type: 'optimize'
        }
      ],
      confidence: {
        overall_score: 90,
        data_quality_score: 95,
        model_certainty: 88,
        last_trained: '2026-06-30T00:00:00Z'
      }
    };

    const domain = mapDashboardSummary(dto);

    expect(domain.tenantId).toBe('t-1');
    expect(domain.sectorId).toBe('s-1');
    expect(domain.lastUpdated).toBe('2026-07-01T00:00:00Z');
    
    expect(domain.kpis[0].id).toBe('k1');
    expect(domain.kpis[0].trend.direction).toBe('up');
    
    expect(domain.forecasts[0].predictedValue).toBe(1200);
    expect(domain.forecasts[0].confidenceLower).toBe(1100);
    
    expect(domain.anomalies[0].deviationScore).toBe(4.5);
    expect(domain.anomalies[0].detectedAt).toBe('2026-07-01T08:00:00Z');
    
    expect(domain.recommendations[0].impactScore).toBe(95);
    expect(domain.recommendations[0].effortLevel).toBe('low');
    
    expect(domain.confidence.overallScore).toBe(90);
    expect(domain.confidence.lastTrained).toBe('2026-06-30T00:00:00Z');
  });

  it('maps empty arrays correctly', () => {
    const dto: DashboardSummaryDTO = {
      tenant_id: 't-2',
      sector_id: 's-2',
      last_updated: '2026-07-01T00:00:00Z',
      kpis: [],
      forecasts: [],
      anomalies: [],
      recommendations: [],
      confidence: {
        overall_score: 0,
        data_quality_score: 0,
        model_certainty: 0,
        last_trained: '2026-06-30T00:00:00Z'
      }
    };

    const domain = mapDashboardSummary(dto);
    expect(domain.kpis).toHaveLength(0);
    expect(domain.forecasts).toHaveLength(0);
    expect(domain.anomalies).toHaveLength(0);
    expect(domain.recommendations).toHaveLength(0);
  });
});
