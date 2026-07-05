import { apiClient } from '@/services/apiClient';
import type { SimulationAnalysisDTO } from '@/types/simulation';

export const simulationClient = {
  getSimulationAnalysis: async (
    tenantId: string,
    sectorId: string,
  ): Promise<SimulationAnalysisDTO> => {
    if (!tenantId || !sectorId) {
      throw new Error('Tenant ID and Sector ID are required');
    }
    const response = await apiClient.get<SimulationAnalysisDTO>(
      `/sectors/${sectorId}/simulations`,
    );
    const dto = response.data;
    if (dto.tenant_id && dto.tenant_id !== tenantId) {
      throw new Error('Tenant isolation boundary violation');
    }
    if (dto.sector_id && dto.sector_id !== sectorId) {
      throw new Error('Sector isolation boundary violation');
    }
    return dto;
  },
};
