import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { EvidenceGraph } from '../EvidenceGraph';

describe('EvidenceGraph', () => {
  it('renders simplified view when nodes > 100', () => {
    const nodes = Array.from({ length: 101 }).map((_, i) => ({
      id: `${i}`, source: 's', description: 'd', reliability: 0.5
    }));
    
    const { getByText } = render(<EvidenceGraph nodes={nodes} edges={[]} onNodeClick={vi.fn()} />);
    
    expect(getByText('Graph visualization hidden because node count exceeds 100. Displaying accessible tabular data instead.')).toBeInTheDocument();
  });

  it('renders normal view when nodes <= 100', () => {
    const nodes = [{ id: '1', source: 'S1', description: 'D1', reliability: 0.8 }];
    const { getByText } = render(<EvidenceGraph nodes={nodes} edges={[]} onNodeClick={vi.fn()} />);
    
    // ECharts is a canvas but we should see the screen reader table
    expect(getByText('S1')).toBeInTheDocument();
  });
});
