import { useQuery } from '@tanstack/react-query';
import { governanceClient } from '../api/governanceClient';
import { mapGovernancePermission } from '../api/governanceMapper';
import { queryKeys } from '@/lib/queryKeys';

export function usePermissions(tenantId: string, role: string) {
  return useQuery({
    queryKey: queryKeys.admin.permissions(tenantId, role),
    queryFn: () => governanceClient.getPermissions(tenantId, role),
    select: (data) => data.map(mapGovernancePermission),
    retry: 1,
    staleTime: 5 * 60 * 1000,
    enabled: Boolean(tenantId && role),
  });
}
