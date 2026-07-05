import { describe, it, expect, vi } from 'vitest';
import type { Mock } from 'vitest';
import { render, waitFor } from '@/utils/test-utils';
import { DashboardPage } from '../pages/DashboardPage';
import { useDashboard } from '../hooks/useDashboard';

vi.mock('../hooks/useDashboard', () => ({
  useDashboard: vi.fn(),
}));

describe('DashboardPage', () => {
  it('renders loading state', () => {
    (useDashboard as Mock).mockReturnValue({ isLoading: true });
    const { getByText } = render(<DashboardPage />);
    expect(getByText('Loading Executive Dashboard...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    (useDashboard as Mock).mockReturnValue({ isError: true, data: null });
    const { getByText } = render(<DashboardPage />);
    expect(getByText('Failed to load dashboard data.')).toBeInTheDocument();
  });

  it('renders WHAT, WHY, WILL, SHOULD sections with data', async () => {
    const mockData = {
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
    };

    (useDashboard as Mock).mockReturnValue({ data: mockData, isLoading: false, isError: false });
    
    const { getByText } = render(<DashboardPage />);
    
    await waitFor(() => {
      expect(getByText('WHAT Happened')).toBeInTheDocument();
      expect(getByText('WHY It Happened')).toBeInTheDocument();
      expect(getByText('WILL It Happen')).toBeInTheDocument();
      expect(getByText('SHOULD We Act')).toBeInTheDocument();
      
      expect(getByText('Revenue')).toBeInTheDocument();
      expect(getByText('Anomaly: Orders')).toBeInTheDocument();
      expect(getByText('Revenue Forecast')).toBeInTheDocument();
      expect(getByText('Fix It')).toBeInTheDocument();
    });
  });
});
