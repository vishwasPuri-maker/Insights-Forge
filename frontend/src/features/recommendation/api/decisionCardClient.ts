import { apiClient } from '@/services/apiClient';
import type { DecisionCardDTO, DecisionCard } from '@/types/decisionCard';
import { mapDecisionCard } from '@/types/decisionCard';

interface ListParams {
  status?: string;
  limit?: number;
  offset?: number;
}

export const decisionCardClient = {
  // GET /api/v1/decision-cards
  list: async (params: ListParams = {}): Promise<DecisionCard[]> => {
    const { data } = await apiClient.get<DecisionCardDTO[]>('/decision-cards', { params });
    return data.map(mapDecisionCard);
  },

  // POST /api/v1/decision-cards/{card_id}/approve
  approve: async (cardId: string): Promise<DecisionCard> => {
    const { data } = await apiClient.post<DecisionCardDTO>(`/decision-cards/${cardId}/approve`);
    return mapDecisionCard(data);
  },

  // POST /api/v1/decision-cards/{card_id}/reject
  reject: async (cardId: string): Promise<DecisionCard> => {
    const { data } = await apiClient.post<DecisionCardDTO>(`/decision-cards/${cardId}/reject`);
    return mapDecisionCard(data);
  },
};
