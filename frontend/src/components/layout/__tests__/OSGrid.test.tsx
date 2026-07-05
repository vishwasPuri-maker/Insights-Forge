import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import '@testing-library/jest-dom';
import { OSGrid } from '../OSGrid';

describe('OSGrid', () => {
  it('renders children inside grid container', () => {
    const { getByText } = render(
      <OSGrid>
        <div>Item 1</div>
        <div>Item 2</div>
      </OSGrid>
    );

    expect(getByText('Item 1')).toBeInTheDocument();
    expect(getByText('Item 2')).toBeInTheDocument();
  });

  it('has no accessibility violations', async () => {
    const { container } = render(
      <OSGrid>
        <div>Item 1</div>
      </OSGrid>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
