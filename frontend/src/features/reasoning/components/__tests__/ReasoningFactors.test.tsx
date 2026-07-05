import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { ReasoningFactors } from '../ReasoningFactors';
import type { ReasoningFactor } from '@/types/reasoning';

describe('ReasoningFactors', () => {
  it('renders factors correctly', () => {
    const factors: ReasoningFactor[] = [{
      id: '1', name: 'F1', contributionWeight: 0.75, trend: 'increasing'
    }];
    
    const { getByText } = render(<ReasoningFactors factors={factors} />);
    
    expect(getByText('F1')).toBeInTheDocument();
    expect(getByText('75%')).toBeInTheDocument();
    expect(getByText('increasing')).toBeInTheDocument();
  });
});
