import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { RecommendationPanel } from '../RecommendationPanel';
import type { ReasoningRecommendation } from '@/types/reasoning';

describe('RecommendationPanel', () => {
  it('renders recommendations with status roles', () => {
    const recs: ReasoningRecommendation[] = [{
      id: '1', title: 'R1', description: 'D1', impactScore: 0.9, effortLevel: 'low', actionType: 'optimize'
    }];
    
    const { getByRole, getByText } = render(<RecommendationPanel recommendations={recs} />);
    
    expect(getByRole('status')).toBeInTheDocument();
    expect(getByText('R1')).toBeInTheDocument();
    expect(getByText('D1')).toBeInTheDocument();
  });
});
