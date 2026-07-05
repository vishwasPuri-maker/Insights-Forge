// Matches DecisionCardOut in openapi.json.
export interface DecisionCardDTO {
  id: string;
  sector: string;
  title: string;
  recommendation?: string | null;
  confidence_score?: number | null;
  status: string;
  resolved_by?: string | null;
  resolved_at?: string | null;
  created_at: string;
}

// Domain model (camelCase) consumed by the UI.
export interface DecisionCard {
  id: string;
  sector: string;
  title: string;
  recommendation: string | null;
  confidenceScore: number | null;
  status: string;
  resolvedBy: string | null;
  resolvedAt: string | null;
  createdAt: string;
}

export const mapDecisionCard = (dto: DecisionCardDTO): DecisionCard => ({
  id: dto.id,
  sector: dto.sector,
  title: dto.title,
  recommendation: dto.recommendation ?? null,
  confidenceScore: dto.confidence_score ?? null,
  status: dto.status,
  resolvedBy: dto.resolved_by ?? null,
  resolvedAt: dto.resolved_at ?? null,
  createdAt: dto.created_at,
});
