// ---------------------------------------------------------------------------
// DTO Models — match openapi.json exactly.
// The dashboard is assembled from two real endpoints:
//   GET /api/v1/sectors/{sector}/scorecard  -> ScorecardOut
//   GET /api/v1/sectors/{sector}/timeseries -> TimeseriesOut
// The backend does NOT expose forecasts / anomalies / recommendations /
// confidence for the dashboard, so those domain fields are left empty.
// ---------------------------------------------------------------------------

export interface ScorecardCardDTO {
  key: string;
  label: string;
  value?: number | string | null;
  unit?: string | null;
}

export interface ScorecardOut {
  sector: string;
  cards: ScorecardCardDTO[];
}

export interface TimeseriesSeriesDTO {
  name: string;
  values: number[];
}

export interface TimeseriesOut {
  sector: string;
  labels: string[];
  series: TimeseriesSeriesDTO[];
}

// ---------------------------------------------------------------------------
// Domain Models (Frontend Representation)
// ---------------------------------------------------------------------------

export interface KPI {
  id: string;
  title: string;
  value: number;
  unit: string;
  trend: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
    label: string;
  };
}

export interface Forecast {
  id: string;
  metric: string;
  predictedValue: number;
  confidenceLower: number;
  confidenceUpper: number;
  targetDate: string;
}

export interface Anomaly {
  id: string;
  metric: string;
  deviationScore: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  detectedAt: string;
  description: string;
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  impactScore: number;
  effortLevel: 'low' | 'medium' | 'high';
  actionType: 'optimize' | 'mitigate' | 'investigate';
}

export interface TimeseriesChart {
  labels: string[];
  series: { name: string; values: number[] }[];
}

export interface DashboardSummary {
  sectorId: string;
  kpis: KPI[];
  timeseries: TimeseriesChart;
  // Not provided by the current backend contract — kept empty for the UI.
  forecasts: Forecast[];
  anomalies: Anomaly[];
  recommendations: Recommendation[];
}
