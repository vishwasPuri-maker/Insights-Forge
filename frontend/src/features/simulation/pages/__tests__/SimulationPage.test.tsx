import { render, screen, fireEvent } from '@testing-library/react';
import { SimulationPage } from '../SimulationPage';
import { describe, it, expect, vi } from 'vitest';
import { useSimulate } from '../../hooks/useSimulate';

vi.mock('../../hooks/useSimulate');

const mockResult = {
  sector: 'retail',
  projections: [
    { key: 'revenue', current: 10000, projected: 10500, change_pct: 5 },
    { key: 'units', current: 500, projected: 490, change_pct: -2 },
  ],
  total_current: 10500,
  total_projected: 10990,
};

describe('SimulationPage', () => {
  it('renders Scenario Simulation page and handles input/simulation run', () => {
    const mockMutate = vi.fn();
    vi.mocked(useSimulate).mockReturnValue({
      mutate: mockMutate,
      data: undefined,
      isPending: false,
      isError: false,
      error: null,
    } as any);

    render(<SimulationPage />);

    // Expect layout elements to be present
    expect(screen.getByText('Scenario Simulation OS')).toBeInTheDocument();
    expect(screen.getByDisplayValue('revenue')).toBeInTheDocument();

    // Trigger run simulation
    const runBtn = screen.getByRole('button', { name: /Run simulation/i });
    fireEvent.click(runBtn);

    expect(mockMutate).toHaveBeenCalledWith({
      metrics: [
        { key: 'revenue', current: 10000, change_pct: 5 },
        { key: 'units', current: 500, change_pct: -2 },
      ],
    });
  });

  it('renders projected results on success', () => {
    vi.mocked(useSimulate).mockReturnValue({
      mutate: vi.fn(),
      data: mockResult,
      isPending: false,
      isError: false,
      error: null,
    } as any);

    render(<SimulationPage />);

    // Projection section should be visible
    expect(screen.getByText('Projections')).toBeInTheDocument();
    expect(screen.getByText('Sector: retail · Total 10,500 → 10,990')).toBeInTheDocument();
    expect(screen.getByText('revenue')).toBeInTheDocument();
    expect(screen.getByText('10,500')).toBeInTheDocument();
    expect(screen.getByText('+5%')).toBeInTheDocument();
    expect(screen.getByText('-2%')).toBeInTheDocument();
  });

  it('renders error state on failure', () => {
    vi.mocked(useSimulate).mockReturnValue({
      mutate: vi.fn(),
      data: undefined,
      isPending: false,
      isError: true,
      error: new Error('Simulation failed unexpectedly'),
    } as any);

    render(<SimulationPage />);

    expect(screen.getByText('Simulation failed unexpectedly')).toBeInTheDocument();
  });
});
