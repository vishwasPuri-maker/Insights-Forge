import { describe, it, expect } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useGovernance } from '../hooks/useGovernance';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

const queryClient = new QueryClient();

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('governanceHook', () => {
  it('fetches and maps governance analysis securely', async () => {
    const { result } = renderHook(() => useGovernance('t1', 'Admin'), { wrapper });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.tenantId).toBe('t1');
    expect(result.current.data?.summary.activeUsers).toBe(120);
  });

  it('disables query if tenantId is missing', () => {
    const { result } = renderHook(() => useGovernance('', 'Admin'), { wrapper });
    expect(result.current.fetchStatus).toBe('idle');
  });
});
