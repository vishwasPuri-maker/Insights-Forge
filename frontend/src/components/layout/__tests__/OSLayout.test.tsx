import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import '@testing-library/jest-dom';
import { OSLayout } from '../OSLayout';

describe('OSLayout', () => {
  it('renders title, description, and children correctly', () => {
    const { getByText } = render(
      <OSLayout title="Test Title" description="Test Description">
        <div data-testid="child">Child Content</div>
      </OSLayout>
    );

    expect(getByText('Test Title')).toBeInTheDocument();
    expect(getByText('Test Description')).toBeInTheDocument();
    expect(getByText('Child Content')).toBeInTheDocument();
  });

  it('has no accessibility violations', async () => {
    const { container } = render(
      <OSLayout title="Test Title" description="Test Description">
        <div>Child Content</div>
      </OSLayout>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
