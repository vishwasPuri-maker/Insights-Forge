import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { GovernancePage } from '../pages/GovernancePage';
import { useGovernance } from '../hooks/useGovernance';
import { useAuthStore } from '@/store/authStore';
import { useTenantStore } from '@/store/tenantStore';

vi.mock('../hooks/useGovernance');
vi.mock('@/store/authStore');
vi.mock('@/store/tenantStore');
vi.mock('@/components/charts/BaseChart', () => ({
  BaseChart: () => <div data-testid="mock-chart" />
}));

describe('GovernancePage', () => {
  it('renders loading state initially', () => {
    vi.mocked(useAuthStore).mockReturnValue({ role: 'Admin' } as any);
    vi.mocked(useTenantStore).mockReturnValue({ tenantId: 't1' } as any);
    vi.mocked(useGovernance).mockReturnValue({ isLoading: true, isError: false, data: undefined } as any);

    const { getByText } = render(<GovernancePage />);
    expect(getByText(/Initializing Governance Operating System/i)).toBeInTheDocument();
  });
});
