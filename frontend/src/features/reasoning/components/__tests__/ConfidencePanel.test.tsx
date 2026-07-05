import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { ConfidencePanel } from '../ConfidencePanel';

describe('ConfidencePanel', () => {
  it('renders progress bar correctly based on score', () => {
    const { getByRole, getByText } = render(<ConfidencePanel score={0.72} />);
    
    const pb = getByRole('progressbar');
    expect(pb).toHaveAttribute('aria-valuenow', '72');
    expect(getByText('72%')).toBeInTheDocument();
  });
});
