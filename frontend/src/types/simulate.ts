// Matches SimulateRequest / SimulateResponse in openapi.json.

export interface SimulateMetric {
  key: string;
  current: number;
  change_pct?: number;
}

export interface SimulateRequest {
  metrics: SimulateMetric[];
}

export interface SimulateProjection {
  key: string;
  current: number;
  projected: number;
  change_pct: number;
}

export interface SimulateResponse {
  sector: string;
  projections: SimulateProjection[];
  total_current: number;
  total_projected: number;
}
