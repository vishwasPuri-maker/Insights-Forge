import { apiClient } from './apiClient';
import type { DatasetMetadata } from '@/types/dataset';

export const datasetClient = {
  // GET /api/v1/datasets -> DatasetOut[] (paginated via limit/offset query params).
  // Datasets are scoped to the caller's tenant by the backend, not by sector path.
  getDatasets: async (limit = 50, offset = 0): Promise<DatasetMetadata[]> => {
    const { data } = await apiClient.get<DatasetMetadata[]>('/datasets', {
      params: { limit, offset },
    });
    return data;
  },

  // GET /api/v1/datasets/{dataset_id}
  getDataset: async (datasetId: string): Promise<DatasetMetadata> => {
    const { data } = await apiClient.get<DatasetMetadata>(`/datasets/${datasetId}`);
    return data;
  },
};
