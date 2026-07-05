import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import { SimulationLoadingState } from '../components/SimulationLoadingState';
import { SimulationRunningState } from '../components/SimulationRunningState';
import { SimulationForecastChart } from '../components/SimulationForecastChart';
import { SimulationParametersPanel } from '../components/SimulationParametersPanel';
import { describe, it, expect } from 'vitest';

describe('SimulationAccessibility', () => {
  it('Loading state has no violations and correct aria', async () => {
    const { container } = render(<SimulationLoadingState />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    expect(container.querySelector('[aria-busy="true"]')).toBeInTheDocument();
    expect(container.querySelector('[role="status"]')).toBeInTheDocument();
  });

  it('Running state has no violations and correct aria', async () => {
    const { container } = render(<SimulationRunningState />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    expect(container.querySelector('[aria-busy="true"]')).toBeInTheDocument();
  });

  it('Parameters panel has proper slider attributes', async () => {
    const params = [{ id: 'p1', name: 'Price', currentValue: 10, proposedValue: 15, bounds: [0, 100] as [number, number], unit: '$' }];
    const { container } = render(<SimulationParametersPanel parameters={params} onParametersChange={() => {}} />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
    
    const slider = container.querySelector('input[type="range"]');
    expect(slider).toHaveAttribute('aria-valuemin', '0');
    expect(slider).toHaveAttribute('aria-valuemax', '100');
    expect(slider).toHaveAttribute('aria-valuenow', '15');
  });

  it('Chart wrapper enforces hidden semantics', () => {
    const { container } = render(<SimulationForecastChart forecasts={[]} />);
    const chart = container.querySelector('[aria-hidden="true"]');
    expect(chart).toBeInTheDocument();
  });
});
