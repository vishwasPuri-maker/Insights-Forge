import { apiClient } from '@/services/apiClient';
import type { TimeseriesOut } from '@/types/dashboard';

export interface MarketTimeseries {
  labels: string[];
  series: { name: string; values: number[] }[];
}

// Read-only market/benchmark series from the dedicated market workspace
// (GET /sectors/{sector}/market/timeseries — additive endpoint). Returns
// empty labels when the feature is disabled server-side.
export const marketClient = {
  async getMarketTimeseries(sectorId: string): Promise<MarketTimeseries> {
    const { data } = await apiClient.get<TimeseriesOut>(
      `/sectors/${sectorId}/market/timeseries`,
    );
    return {
      labels: data.labels ?? [],
      series: (data.series ?? []).map((s) => ({ name: s.name, values: s.values ?? [] })),
    };
  },
};

// Trigger a live market-data refresh (scrape) for the sector, then return the
// fresh series. Backs the "Compare with market" action — may take time.
export async function refreshMarketTimeseries(sectorId: string): Promise<MarketTimeseries> {
  const { data } = await apiClient.post<TimeseriesOut>(
    `/sectors/${sectorId}/market/refresh`,
  );
  return {
    labels: data.labels ?? [],
    series: (data.series ?? []).map((s) => ({ name: s.name, values: s.values ?? [] })),
  };
}
