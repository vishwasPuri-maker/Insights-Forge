import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import '@testing-library/jest-dom';
import { OSSection } from '../OSSection';

describe('OSSection', () => {
  it('renders semantic section with title and description', () => {
    const { getByRole, getByText } = render(
      <OSSection title="Section Title" description="Section Desc">
        <div>Content</div>
      </OSSection>
    );

    const heading = getByRole('heading', { level: 2 });
    expect(heading).toHaveTextContent('Section Title');
    expect(getByText('Section Desc')).toBeInTheDocument();
    expect(getByText('Content')).toBeInTheDocument();
  });

  it('has no accessibility violations', async () => {
    const { container } = render(
      <OSSection title="Section Title" description="Section Desc">
        <div>Content</div>
      </OSSection>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
