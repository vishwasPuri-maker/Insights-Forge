import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/react';
import { EvidenceInspector } from '../EvidenceInspector';

describe('EvidenceInspector', () => {
  it('returns null when evidence is null', () => {
    const { container } = render(<EvidenceInspector evidence={null} onClose={vi.fn()} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders evidence details and calls onClose', () => {
    const evidence = { id: '1', source: 'S1', description: 'D1', reliability: 0.9 };
    const onClose = vi.fn();
    const { getByText, getByRole } = render(<EvidenceInspector evidence={evidence} onClose={onClose} />);
    
    expect(getByText('S1')).toBeInTheDocument();
    expect(getByText('D1')).toBeInTheDocument();
    
    fireEvent.click(getByRole('button', { name: /close/i }));
    expect(onClose).toHaveBeenCalled();
  });
});
