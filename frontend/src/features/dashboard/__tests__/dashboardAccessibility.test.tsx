import { describe, it, expect, vi } from 'vitest';
import type { Mock } from 'vitest';
import { render } from '@/utils/test-utils';
import { axe } from 'jest-axe';
import { DashboardPage } from '../pages/DashboardPage';
import { useDashboard } from '../hooks/useDashboard';

vi.mock('../hooks/useDashboard', () => ({
  useDashboard: vi.fn(),
}));

describe('dashboardAccessibility', () => {
  it('DashboardPage has no accessibility violations', async () => {
    (useDashboard as Mock).mockReturnValue({
      data: {
        kpis: [
          { id: 'k1', title: 'Revenue', value: 1000, unit: '$', trend: { value: 10, direction: 'up', label: 'vs yesterday' } }
        ],
        anomalies: [
          { id: 'a1', metric: 'Orders', deviationScore: 2.1, severity: 'low', detectedAt: '2026-01-01', description: 'Desc' }
        ],
        forecasts: [
          { id: 'f1', metric: 'Revenue', predictedValue: 1200, confidenceLower: 1100, confidenceUpper: 1300, targetDate: '2026-01-02' }
        ],
        recommendations: [
          { id: 'r1', title: 'Fix It', description: 'Desc', impactScore: 80, effortLevel: 'low', actionType: 'optimize' }
        ],
      },
      isLoading: false,
      isError: false
    });

    const { container } = render(<DashboardPage />);
    const results = await axe(container);
    
    // Some echarts canvas elements might fail contrast checking depending on JSDOM,
    // but structure should be clear.
    expect(results).toHaveNoViolations();
  });
});
