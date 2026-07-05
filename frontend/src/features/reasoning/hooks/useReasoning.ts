import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { reasoningClient } from '../api/reasoningClient';
import { mapReasoningAnalysis } from '../api/reasoningMapper';
import type { ReasoningAnalysis, ReasoningAnalysisDTO } from '@/types/reasoning';
import type { AxiosError } from 'axios';
import type { ApiErrorResponse } from '@/types/api';

export function useReasoning(tenantId: string | null, sectorId: string | null) {
  return useQuery<ReasoningAnalysisDTO, AxiosError<ApiErrorResponse>, ReasoningAnalysis>({
    queryKey: sectorId && tenantId ? queryKeys.sector.reasoning(tenantId, sectorId) : [],
    queryFn: async () => {
      if (!tenantId || !sectorId) {
        throw new Error('Missing tenant or sector context');
      }
      return reasoningClient.getReasoningAnalysis(tenantId, sectorId);
    },
    enabled: Boolean(tenantId && sectorId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
    retry: 1,
    select: (data) => mapReasoningAnalysis(data),
  });
}
