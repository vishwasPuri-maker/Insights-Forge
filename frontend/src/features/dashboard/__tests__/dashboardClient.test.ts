import { describe, it, expect, vi } from 'vitest';
import type { Mock } from 'vitest';
import { dashboardClient } from '../api/dashboardClient';
import { apiClient } from '@/services/apiClient';

vi.mock('@/services/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
  }
}));

describe('dashboardClient', () => {
  it('fetches and maps the dashboard summary', async () => {
    const mockDTO = {
      tenant_id: 't1',
      sector_id: 's1',
      kpis: [],
      forecasts: [],
      anomalies: [],
      recommendations: [],
      confidence: { overall_score: 90 },
      last_updated: '2026-07-01'
    };

    (apiClient.get as Mock).mockResolvedValue({ data: mockDTO });

    const result = await dashboardClient.getDashboardSummary('s1');

    expect(apiClient.get).toHaveBeenCalledWith('/sectors/s1/dashboard');
    expect(result.tenantId).toBe('t1');
    expect(result.sectorId).toBe('s1');
    expect(result.confidence.overallScore).toBe(90);
  });
});
