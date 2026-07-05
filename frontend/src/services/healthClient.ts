import { apiClient } from './apiClient';

export const healthClient = {
  // GET /api/v1/health — liveness probe.
  check: async (): Promise<unknown> => {
    const { data } = await apiClient.get('/health');
    return data;
  },
};
