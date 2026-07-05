import { describe, it, expect } from 'vitest';
import { render, fireEvent } from '@testing-library/react';
import { ReasoningInsights } from '../ReasoningInsights';
import type { ReasoningInsight } from '@/types/reasoning';

describe('ReasoningInsights', () => {
  it('renders tree structure and expands on click', () => {
    const insights: ReasoningInsight[] = [{
      id: '1', title: 'I1', description: 'D1', severity: 'critical', category: 'anomaly'
    }];
    
    const { getByText, getByRole, queryByText } = render(<ReasoningInsights insights={insights} />);
    
    expect(getByRole('tree')).toBeInTheDocument();
    const item = getByRole('treeitem');
    expect(item).toHaveAttribute('aria-expanded', 'false');
    expect(queryByText('D1')).not.toBeInTheDocument();
    
    const button = getByRole('button');
    fireEvent.click(button);
    
    expect(item).toHaveAttribute('aria-expanded', 'true');
    expect(getByText('D1')).toBeInTheDocument();
  });
});
