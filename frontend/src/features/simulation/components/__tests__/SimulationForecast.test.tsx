import { render, screen } from '@testing-library/react';
import { SimulationForecastChart } from '../SimulationForecastChart';
import { describe, it, expect } from 'vitest';
import type { SimulationForecast } from '@/types/simulation';

describe('SimulationForecastChart', () => {
  const mockForecast: SimulationForecast[] = Array.from({ length: 10 }, (_, i) => ({
    id: `f-${i}`,
    metric: 'Revenue',
    targetDate: `2026-01-${String(i + 1).padStart(2, '0')}`,
    predictedValue: 100 + i,
    confidenceLower: 90 + i,
    confidenceUpper: 110 + i
  }));

  it('renders BaseChart wrapper with aria-hidden', () => {
    const { container } = render(<SimulationForecastChart forecasts={mockForecast} />);
    const chartContainer = container.querySelector('[aria-hidden="true"]');
    expect(chartContainer).toBeInTheDocument();
  });

  it('renders ExecutiveTable fallback', () => {
    render(<SimulationForecastChart forecasts={mockForecast} />);
    expect(screen.getByRole('table', { name: /Forecast Details/i })).toBeInTheDocument();
    expect(screen.getByText('2026-01-01')).toBeInTheDocument();
  });

  it('enforces 1000 point limit safety guard', () => {
    const massiveForecast: SimulationForecast[] = Array.from({ length: 1001 }, (_, i) => ({
      id: `m-${i}`,
      metric: 'Revenue',
      targetDate: `2026-01-01`,
      predictedValue: 100,
      confidenceLower: 90,
      confidenceUpper: 110
    }));

    render(<SimulationForecastChart forecasts={massiveForecast} />);
    expect(screen.getByText(/Forecast data points exceed safety limit/i)).toBeInTheDocument();
  });
});
