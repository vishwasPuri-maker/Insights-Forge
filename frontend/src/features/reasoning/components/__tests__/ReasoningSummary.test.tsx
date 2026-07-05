import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { ReasoningSummary } from '../ReasoningSummary';

describe('ReasoningSummary', () => {
  it('renders summary domain correctly', () => {
    const summary = {
      topic: 'Topic 1',
      executiveSummary: 'Exec summary',
      primaryConclusion: 'Primary conc'
    };
    
    const { getByText } = render(<ReasoningSummary summary={summary} confidenceScore={80} />);
    
    expect(getByText('Topic 1')).toBeInTheDocument();
    expect(getByText('Exec summary')).toBeInTheDocument();
    expect(getByText('Primary conc')).toBeInTheDocument();
    expect(getByText('80%')).toBeInTheDocument();
  });
});
