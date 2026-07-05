import { useMutation, useQuery } from '@tanstack/react-query';
import { reportsClient } from '../api/reportsClient';
import { useTenantStore } from '@/store/tenantStore';
import { queryKeys } from '@/lib/queryKeys';
import type { ReportCompileRequest } from '@/types/report';

export function useCompileReport() {
  return useMutation({
    mutationFn: (body: ReportCompileRequest) => reportsClient.compile(body),
  });
}

export function useReport(reportId: string | null) {
  const { tenantId } = useTenantStore();
  return useQuery({
    queryKey: queryKeys.reports.detail(tenantId ?? '', reportId ?? ''),
    queryFn: () => reportsClient.get(reportId!),
    enabled: !!reportId,
    // Poll while the report is still compiling.
    refetchInterval: (query) =>
      query.state.data && query.state.data.status.toLowerCase() === 'ready' ? false : 3000,
  });
}
