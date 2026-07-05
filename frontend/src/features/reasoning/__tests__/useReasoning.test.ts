import { describe, it, expect, vi } from 'vitest';
import type { Mock } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useReasoning } from '../hooks/useReasoning';
import { reasoningClient } from '../api/reasoningClient';
import { AllTheProviders } from '@/utils/test-utils';

vi.mock('../api/reasoningClient', () => ({
  reasoningClient: {
    getReasoningAnalysis: vi.fn(),
  },
}));

describe('useReasoning', () => {
  it('fetches and maps reasoning analysis when context is available', async () => {
    const mockDTO = {
      id: 'ra-1',
      tenant_id: 't-1',
      sector_id: 's-1',
      summary: { topic: 'A', executive_summary: 'B', primary_conclusion: 'C' },
      insights: [],
      factors: [],
      evidence_nodes: [],
      evidence_edges: [],
      recommendations: [],
      confidence: { overall_score: 1, data_quality_score: 1, model_certainty: 1 },
      metadata: { generated_at: 'X', model_id: 'Y', processing_time_ms: 100 }
    };

    (reasoningClient.getReasoningAnalysis as Mock).mockResolvedValue(mockDTO);

    const { result } = renderHook(() => useReasoning('t-1', 's-1'), { wrapper: AllTheProviders });
    
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    
    expect(result.current.data).toBeDefined();
    expect(result.current.data?.tenantId).toBe('t-1');
  });

  it('throws an error if tenant or sector is missing', async () => {
    const { result } = renderHook(() => useReasoning(null, null), { wrapper: AllTheProviders });
    expect(result.current.isPending).toBe(true);
    expect(result.current.fetchStatus).toBe('idle');
  });
});
