import { apiClient } from '@/services/apiClient';
import type { ReasoningAnalysisDTO } from '@/types/reasoning';

export const reasoningClient = {
  getReasoningAnalysis: async (
    tenantId: string,
    sectorId: string,
  ): Promise<ReasoningAnalysisDTO> => {
    const response = await apiClient.get<ReasoningAnalysisDTO>(
      `/sectors/${sectorId}/reasoning`,
    );
    const dto = response.data;
    if (dto.tenant_id && dto.tenant_id !== tenantId) {
      throw new Error('Tenant isolation violation detected in response payload');
    }
    return dto;
  },
};
