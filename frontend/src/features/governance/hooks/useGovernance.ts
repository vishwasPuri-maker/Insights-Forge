import { useQuery } from '@tanstack/react-query';
import { governanceClient } from '../api/governanceClient';
import { mapGovernanceAnalysis } from '../api/governanceMapper';
import { queryKeys } from '@/lib/queryKeys';

export function useGovernance(tenantId: string, role: string) {
  return useQuery({
    queryKey: queryKeys.admin.analysis(tenantId, role),
    queryFn: () => governanceClient.getGovernanceAnalysis(tenantId, role),
    select: mapGovernanceAnalysis,
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
    enabled: Boolean(tenantId && role),
  });
}
