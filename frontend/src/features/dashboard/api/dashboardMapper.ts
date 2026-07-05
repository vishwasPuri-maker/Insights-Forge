import type {
  ScorecardOut,
  TimeseriesOut,
  DashboardSummary,
  KPI,
} from '@/types/dashboard';

// A scorecard card value may be a number, a preformatted string, or null.
// KPIWidget renders numbers, so coerce non-numeric values to 0 and keep the
// original unit for display.
const toNumber = (value: number | string | null | undefined): number => {
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const parsed = parseFloat(value.replace(/[^0-9.-]/g, ''));
    return Number.isNaN(parsed) ? 0 : parsed;
  }
  return 0;
};

export const mapScorecardToKpis = (dto: ScorecardOut): KPI[] =>
  dto.cards.map((card) => ({
    id: card.key,
    title: card.label,
    value: toNumber(card.value),
    unit: card.unit ?? '',
    // The backend scorecard has no trend data; render a neutral placeholder.
    trend: { value: 0, direction: 'neutral' as const, label: '' },
  }));

export const mapDashboardSummary = (
  scorecard: ScorecardOut,
  timeseries: TimeseriesOut,
): DashboardSummary => ({
  sectorId: scorecard.sector,
  kpis: mapScorecardToKpis(scorecard),
  timeseries: {
    labels: timeseries.labels,
    series: timeseries.series.map((s) => ({ name: s.name, values: s.values })),
  },
  // Not available from the current backend contract.
  forecasts: [],
  anomalies: [],
  recommendations: [],
});
