import { apiClient } from '@/services/apiClient';
import type { ThresholdOut, ThresholdUpdate } from '@/types/threshold';

export const thresholdClient = {
  // GET /api/v1/thresholds
  list: async (): Promise<ThresholdOut[]> => {
    const { data } = await apiClient.get<ThresholdOut[]>('/thresholds');
    return data;
  },

  // PUT /api/v1/thresholds/{threshold_id}
  update: async (thresholdId: string, body: ThresholdUpdate): Promise<ThresholdOut> => {
    const { data } = await apiClient.put<ThresholdOut>(`/thresholds/${thresholdId}`, body);
    return data;
  },
};
