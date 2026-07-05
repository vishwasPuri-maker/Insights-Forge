import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { renderHook } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useSimulation } from '../hooks/useSimulation';

vi.mock('../api/simulationClient', () => ({
  simulationClient: {
    getSimulationAnalysis: vi.fn()
  }
}));

describe('useSimulation', () => {
  it('disables query if tenant or sector is missing', () => {
    const queryClient = new QueryClient();
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    const { result } = renderHook(() => useSimulation(null, 's1'), { wrapper });
    expect(result.current.isPending).toBe(true);
    expect(result.current.fetchStatus).toBe('idle');
  });
});
