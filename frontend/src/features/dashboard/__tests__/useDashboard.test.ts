import { describe, it, expect, vi } from 'vitest';
import type { Mock } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useDashboard } from '../hooks/useDashboard';
import { useTenantStore } from '@/store/tenantStore';
import { dashboardClient } from '../api/dashboardClient';
import { AllTheProviders } from '@/utils/test-utils';

vi.mock('../api/dashboardClient', () => ({
  dashboardClient: {
    getDashboardSummary: vi.fn(),
  }
}));

describe('useDashboard', () => {
  it('does not fetch when tenantId or sectorId is missing', () => {
    useTenantStore.setState({ tenantId: null, sectorId: null });
    const { result } = renderHook(() => useDashboard(), { wrapper: AllTheProviders });
    expect(result.current.isPending).toBe(true);
    expect(result.current.fetchStatus).toBe('idle');
  });

  it('fetches data when tenant and sector are set', async () => {
    const mockDomain = { tenantId: 't1', sectorId: 's1' };
    (dashboardClient.getDashboardSummary as Mock).mockResolvedValue(mockDomain);
    
    useTenantStore.setState({ tenantId: 't1', sectorId: 's1' });
    const { result } = renderHook(() => useDashboard(), { wrapper: AllTheProviders });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    
    expect(dashboardClient.getDashboardSummary).toHaveBeenCalledWith('s1');
    expect(result.current.data).toEqual(mockDomain);
  });
});
