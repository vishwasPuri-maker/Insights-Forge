import { render, screen, fireEvent } from '@testing-library/react';
import { SimulationParametersPanel } from '../SimulationParametersPanel';
import { describe, it, expect, vi, beforeEach } from 'vitest';

describe('SimulationInteraction', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  it('debounces parameter changes', async () => {
    const handleChange = vi.fn();
    const params = [{ id: 'p1', name: 'Price', currentValue: 10, proposedValue: 15, bounds: [0, 100] as [number, number], unit: '$' }];
    
    render(<SimulationParametersPanel parameters={params} onParametersChange={handleChange} />);
    
    const slider = screen.getByRole('slider');
    
    // Fire rapid changes
    fireEvent.change(slider, { target: { value: '20' } });
    fireEvent.change(slider, { target: { value: '30' } });
    fireEvent.change(slider, { target: { value: '40' } });

    // Ensure not called immediately
    expect(handleChange).not.toHaveBeenCalled();

    // Fast-forward timers
    vi.advanceTimersByTime(300);

    // Verify called once with final value
    expect(handleChange).toHaveBeenCalledTimes(1);
    expect(handleChange).toHaveBeenCalledWith('p1', 40);
  });
});
