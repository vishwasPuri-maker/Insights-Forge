import { useQuery } from '@tanstack/react-query';
import { governanceClient } from '../api/governanceClient';
import { mapGovernanceAuditEntry } from '../api/governanceMapper';
import { queryKeys } from '@/lib/queryKeys';

export function useAudit(tenantId: string, role: string, filters: string = '') {
  return useQuery({
    queryKey: queryKeys.admin.audit(tenantId, role, filters),
    queryFn: () => governanceClient.getAuditLogs(tenantId, role, filters),
    select: (data) => data.map(mapGovernanceAuditEntry),
    retry: 1,
    staleTime: 5 * 60 * 1000,
    enabled: Boolean(tenantId && role),
  });
}
