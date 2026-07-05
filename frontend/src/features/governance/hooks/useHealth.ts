import { useQuery } from '@tanstack/react-query';
import { governanceClient } from '../api/governanceClient';
import { mapGovernanceHealthMetric } from '../api/governanceMapper';
import { queryKeys } from '@/lib/queryKeys';

export function useHealth(tenantId: string) {
  return useQuery({
    queryKey: queryKeys.admin.health(tenantId),
    queryFn: () => governanceClient.getHealth(tenantId),
    select: (data) => data.map(mapGovernanceHealthMetric),
    retry: 1,
    staleTime: 5 * 60 * 1000,
    enabled: Boolean(tenantId),
  });
}
