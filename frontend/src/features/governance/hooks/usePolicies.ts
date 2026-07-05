import { useQuery } from '@tanstack/react-query';
import { governanceClient } from '../api/governanceClient';
import { mapGovernancePolicy } from '../api/governanceMapper';
import { queryKeys } from '@/lib/queryKeys';

export function usePolicies(tenantId: string) {
  return useQuery({
    queryKey: queryKeys.admin.policies(tenantId),
    queryFn: () => governanceClient.getPolicies(tenantId),
    select: (data) => data.map(mapGovernancePolicy),
    retry: 1,
    staleTime: 5 * 60 * 1000,
    enabled: Boolean(tenantId),
  });
}
