import { apiClient } from '@/services/apiClient';
import type { IngestionResponse } from '@/types/ingestion';

export const ingestionClient = {
  // POST /api/v1/ingestion/stream — multipart form (sector + file).
  upload: async (sector: string, file: File): Promise<IngestionResponse> => {
    const form = new FormData();
    form.append('sector', sector);
    form.append('file', file);
    const { data } = await apiClient.post<IngestionResponse>('/ingestion/stream', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
};
