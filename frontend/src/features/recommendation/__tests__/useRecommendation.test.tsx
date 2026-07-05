import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useRecommendation } from '../hooks/useRecommendation';
import { recommendationClient } from '../recommendationClient';
import type { RecommendationAnalysisDTO } from '@/types/recommendation';

vi.mock('../recommendationClient');

describe('useRecommendation', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    queryClient.clear();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  const mockDTO: RecommendationAnalysisDTO = {
    id: 'r1',
    tenant_id: 't1',
    sector_id: 's1',
    metadata: { generated_at: 'now', model_id: 'm1', processing_time_ms: 10 },
    confidence: { actionability_score: 1, data_quality_score: 1, model_certainty: 1 },
    summary: { topic: 't', executive_summary: 's', primary_conclusion: 'c' },
    recommendations: []
  };

  it('fetches and maps data correctly', async () => {
    vi.mocked(recommendationClient.getAnalysis).mockResolvedValueOnce(mockDTO);
    const { result } = renderHook(() => useRecommendation('t1', 's1'), { wrapper });
    
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.tenantId).toBe('t1'); // verify camelCase transformation
    expect(recommendationClient.getAnalysis).toHaveBeenCalledWith('t1', 's1');
  });

  it('handles API errors', async () => {
    vi.mocked(recommendationClient.getAnalysis).mockRejectedValue(new Error('Network error'));
    const { result } = renderHook(() => useRecommendation('t1', 's1'), { wrapper });
    
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    }, { timeout: 5000 });

    expect(result.current.error?.message).toBe('Network error');
  });
});
