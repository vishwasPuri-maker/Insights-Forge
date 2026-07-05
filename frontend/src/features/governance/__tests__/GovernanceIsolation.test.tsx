import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { GovernancePage } from '../pages/GovernancePage';
import { useGovernance } from '../hooks/useGovernance';
import { useAuthStore } from '@/store/authStore';
import { useTenantStore } from '@/store/tenantStore';
import React from 'react';

vi.mock('../hooks/useGovernance');
vi.mock('@/store/authStore');
vi.mock('@/store/tenantStore');
vi.mock('@/components/charts/BaseChart', () => ({
  BaseChart: () => <div data-testid="mock-chart" />
}));

describe('GovernanceIsolation', () => {
  it('fails safely when user lacks tenant context', () => {
    vi.mocked(useAuthStore).mockReturnValue({ role: 'Admin' } as any);
    vi.mocked(useTenantStore).mockReturnValue({ tenantId: null } as any);
    vi.mocked(useGovernance).mockReturnValue({
      isLoading: false,
      isError: true,
      error: new Error('Unauthorized Tenant Context')
    } as any);

    const { getByText } = render(<GovernancePage />);
    expect(getByText(/Unauthorized Tenant Context/i)).toBeInTheDocument();
  });
});
