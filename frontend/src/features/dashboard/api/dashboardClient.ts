import { apiClient } from '@/services/apiClient';
import type { ScorecardOut, TimeseriesOut, DashboardSummary } from '@/types/dashboard';
import { mapDashboardSummary } from './dashboardMapper';

export const dashboardClient = {
  // Assembles the dashboard from the two real backend endpoints:
  //   GET /api/v1/sectors/{sector}/scorecard
  //   GET /api/v1/sectors/{sector}/timeseries
  getDashboardSummary: async (sectorId: string): Promise<DashboardSummary> => {
    const [scorecard, timeseries] = await Promise.all([
      apiClient.get<ScorecardOut>(`/sectors/${sectorId}/scorecard`),
      apiClient.get<TimeseriesOut>(`/sectors/${sectorId}/timeseries`),
    ]);
    return mapDashboardSummary(scorecard.data, timeseries.data);
  },
};
