// Matches ThresholdOut / ThresholdUpdate in openapi.json.

export interface ThresholdOut {
  id: string;
  sector: string;
  metric_key: string;
  label: string;
  warning_value?: number | null;
  critical_value?: number | null;
}

export interface ThresholdUpdate {
  warning_value?: number | null;
  critical_value?: number | null;
}
