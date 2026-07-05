import { apiClient } from '@/services/apiClient';
import type { SimulateRequest, SimulateResponse } from '@/types/simulate';

export const simulateClient = {
  // POST /api/v1/simulate
  run: async (body: SimulateRequest): Promise<SimulateResponse> => {
    const { data } = await apiClient.post<SimulateResponse>('/simulate', body);
    return data;
  },
};
