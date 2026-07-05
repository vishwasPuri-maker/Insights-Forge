import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { decisionCardClient } from '../api/decisionCardClient';
import { useTenantStore } from '@/store/tenantStore';
import { queryKeys } from '@/lib/queryKeys';

export function useDecisionCards(status?: string) {
  const { tenantId } = useTenantStore();
  return useQuery({
    queryKey: queryKeys.decisionCards.list(tenantId ?? '', status),
    queryFn: () => decisionCardClient.list({ status }),
    enabled: !!tenantId,
    staleTime: 2 * 60 * 1000,
  });
}

export function useResolveDecisionCard() {
  const queryClient = useQueryClient();
  const { tenantId } = useTenantStore();

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: [tenantId ?? '', 'decision-cards'] });

  const approve = useMutation({
    mutationFn: (cardId: string) => decisionCardClient.approve(cardId),
    onSuccess: invalidate,
  });

  const reject = useMutation({
    mutationFn: (cardId: string) => decisionCardClient.reject(cardId),
    onSuccess: invalidate,
  });

  return { approve, reject };
}
