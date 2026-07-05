import { render, screen } from '@testing-library/react';
import { SimulationLoadingState } from '../SimulationLoadingState';
import { SimulationErrorState } from '../SimulationErrorState';
import { SimulationEmptyState } from '../SimulationEmptyState';
import { SimulationRunningState } from '../SimulationRunningState';
import { describe, it, expect } from 'vitest';

describe('SimulationState Components', () => {
  it('renders Loading state correctly', () => {
    render(<SimulationLoadingState />);
    expect(screen.getByText('Loading simulation analysis...')).toBeInTheDocument();
  });

  it('renders Error state correctly', () => {
    render(<SimulationErrorState error={new Error('Test Error')} />);
    expect(screen.getByText('Test Error')).toBeInTheDocument();
  });

  it('renders Empty state correctly', () => {
    render(<SimulationEmptyState />);
    expect(screen.getByText('No Simulation Data')).toBeInTheDocument();
  });

  it('renders Running state correctly', () => {
    render(<SimulationRunningState />);
    expect(screen.getByText('Computing Scenario')).toBeInTheDocument();
  });
});
