import { useQuery } from '@tanstack/react-query';
import { dashboardClient } from '../api/dashboardClient';
import { useTenantStore } from '@/store/tenantStore';
import { queryKeys } from '@/lib/queryKeys';

export const useDashboard = () => {
  const { tenantId, sectorId } = useTenantStore();

  return useQuery({
    queryKey: queryKeys.sector.dashboard(tenantId!, sectorId!),
    queryFn: () => dashboardClient.getDashboardSummary(sectorId!),
    enabled: !!tenantId && !!sectorId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 2,
  });
};
