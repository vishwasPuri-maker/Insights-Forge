import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { recommendationClient } from '../recommendationClient';
import { mapRecommendationAnalysis } from '../recommendationMapper';
import type { RecommendationAnalysis } from '@/types/recommendation';

export function useRecommendation(tenantId: string, sectorId: string) {
  return useQuery<RecommendationAnalysis, Error>({
    queryKey: queryKeys.sector.recommendation(tenantId, sectorId),
    queryFn: async () => {
      if (!tenantId || !sectorId) {
        throw new Error('Tenant ID and Sector ID are required');
      }
      const dto = await recommendationClient.getAnalysis(tenantId, sectorId);
      return mapRecommendationAnalysis(dto);
    },
    enabled: Boolean(tenantId && sectorId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1, // Fail fast after 1 retry for architectural purity
  });
}
