import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { userClient } from '../api/userClient';
import { thresholdClient } from '../api/thresholdClient';
import { useTenantStore } from '@/store/tenantStore';
import { queryKeys } from '@/lib/queryKeys';
import type { UserCreate } from '@/types/user';
import type { ThresholdUpdate } from '@/types/threshold';

export function useAdminUsers() {
  const { tenantId } = useTenantStore();
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.users.list(tenantId ?? ''),
    queryFn: () => userClient.list(),
    enabled: !!tenantId,
  });

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: queryKeys.users.list(tenantId ?? '') });

  const create = useMutation({
    mutationFn: (body: UserCreate) => userClient.create(body),
    onSuccess: invalidate,
  });

  const remove = useMutation({
    mutationFn: (userId: string) => userClient.remove(userId),
    onSuccess: invalidate,
  });

  return { ...query, create, remove };
}

export function useThresholds() {
  const { tenantId } = useTenantStore();
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: queryKeys.thresholds.list(tenantId ?? ''),
    queryFn: () => thresholdClient.list(),
    enabled: !!tenantId,
  });

  const update = useMutation({
    mutationFn: ({ id, body }: { id: string; body: ThresholdUpdate }) =>
      thresholdClient.update(id, body),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: queryKeys.thresholds.list(tenantId ?? '') }),
  });

  return { ...query, update };
}
