export interface ForecastPoint {
  timestamp: string;
  actual?: number;
  predicted: number;
  upper_bound: number;
  lower_bound: number;
}

export interface ForecastModel {
  id: string;
  name: string;
  confidence_score: number;
  points: ForecastPoint[];
}
