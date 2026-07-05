import { apiClient } from '@/services/apiClient';
import type { RecommendationAnalysisDTO } from '@/types/recommendation';

export const recommendationClient = {
  getAnalysis: async (
    tenantId: string,
    sectorId: string,
  ): Promise<RecommendationAnalysisDTO> => {
    const response = await apiClient.get<RecommendationAnalysisDTO>(
      `/tenants/${tenantId}/sectors/${sectorId}/recommendation`,
    );
    return response.data;
  },
};
