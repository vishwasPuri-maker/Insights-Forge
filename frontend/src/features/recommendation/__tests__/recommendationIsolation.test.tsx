import { describe, it, expect } from 'vitest';
import { useRecommendation } from '../hooks/useRecommendation';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

describe('recommendationIsolation', () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('rejects recommendation requests from unauthorized tenant', async () => {
    // MSW handler strictly rejects any tenantId !== 't1'
    const { result } = renderHook(() => useRecommendation('t2', 's1'), { wrapper });
    
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    }, { timeout: 5000 });

    // The API error propagates appropriately through the query
    expect(result.current.error).toBeDefined();
  });
});
