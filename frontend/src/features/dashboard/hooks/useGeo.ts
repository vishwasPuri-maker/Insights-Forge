import { useQuery } from '@tanstack/react-query';
import { geoClient } from '../api/geoClient';
import { useTenantStore } from '@/store/tenantStore';
import { queryKeys } from '@/lib/queryKeys';

export function useGeo() {
  const { tenantId, sectorId } = useTenantStore();
  return useQuery({
    queryKey: queryKeys.sector.geo(tenantId ?? '', sectorId ?? ''),
    queryFn: () => geoClient.get(sectorId!),
    enabled: !!tenantId && !!sectorId,
    staleTime: 5 * 60 * 1000,
  });
}
