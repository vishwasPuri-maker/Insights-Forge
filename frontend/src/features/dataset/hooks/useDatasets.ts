import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { datasetClient } from '@/services/datasetClient';
import { recordsClient } from '../api/recordsClient';
import { ingestionClient } from '../api/ingestionClient';
import { useTenantStore } from '@/store/tenantStore';
import { queryKeys } from '@/lib/queryKeys';

export function useDatasets() {
  const { tenantId } = useTenantStore();
  return useQuery({
    queryKey: queryKeys.datasets.list(tenantId ?? ''),
    queryFn: () => datasetClient.getDatasets(),
    enabled: !!tenantId,
  });
}

export function useRecords() {
  const { tenantId, sectorId } = useTenantStore();
  return useQuery({
    queryKey: queryKeys.sector.records(tenantId ?? '', sectorId ?? ''),
    queryFn: () => recordsClient.list(sectorId!),
    enabled: !!tenantId && !!sectorId,
  });
}

export function useIngestion() {
  const { tenantId, sectorId } = useTenantStore();
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => ingestionClient.upload(sectorId!, file),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: queryKeys.datasets.list(tenantId ?? '') }),
  });
}
