import { apiClient } from '@/services/apiClient';
import type { GeoFeatureCollection } from '@/types/geo';

export const geoClient = {
  // GET /api/v1/sectors/{sector}/geo
  get: async (sector: string, limit = 100): Promise<GeoFeatureCollection> => {
    const { data } = await apiClient.get<GeoFeatureCollection>(`/sectors/${sector}/geo`, {
      params: { limit },
    });
    return data;
  },
};
