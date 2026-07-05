import { apiClient } from '@/services/apiClient';
import type { RecordsPage, RecordOut } from '@/types/record';

export const recordsClient = {
  // GET /api/v1/sectors/{sector}/records
  list: async (sector: string, limit = 25, offset = 0): Promise<RecordsPage> => {
    const { data } = await apiClient.get<RecordsPage>(`/sectors/${sector}/records`, {
      params: { limit, offset },
    });
    return data;
  },

  // GET /api/v1/sectors/{sector}/records/{record_id}
  get: async (sector: string, recordId: string): Promise<RecordOut> => {
    const { data } = await apiClient.get<RecordOut>(`/sectors/${sector}/records/${recordId}`);
    return data;
  },
};
