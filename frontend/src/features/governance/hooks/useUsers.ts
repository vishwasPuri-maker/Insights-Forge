import { useQuery } from '@tanstack/react-query';
import { governanceClient } from '../api/governanceClient';
import { mapGovernanceUser } from '../api/governanceMapper';
import { queryKeys } from '@/lib/queryKeys';

export function useUsers(tenantId: string, role: string, sessionId: string) {
  return useQuery({
    queryKey: queryKeys.admin.users(tenantId, role, sessionId),
    queryFn: () => governanceClient.getUsers(tenantId, role, sessionId),
    select: (data) => data.map(mapGovernanceUser),
    retry: 1,
    staleTime: 5 * 60 * 1000,
    enabled: Boolean(tenantId && role && sessionId),
  });
}
