import { useQuery } from '@tanstack/react-query';
import { marketClient } from '../api/marketClient';
import { useTenantStore } from '@/store/tenantStore';
import { queryKeys } from '@/lib/queryKeys';

// Optional overlay data — errors stay silent (retry once, no UI failure).
export const useMarketTimeseries = () => {
  const { tenantId, sectorId } = useTenantStore();

  return useQuery({
    queryKey: queryKeys.sector.market(tenantId!, sectorId!),
    queryFn: () => marketClient.getMarketTimeseries(sectorId!),
    enabled: !!tenantId && !!sectorId,
    staleTime: 10 * 60 * 1000,
    retry: 1,
  });
};
