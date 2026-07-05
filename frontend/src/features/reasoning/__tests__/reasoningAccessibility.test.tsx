import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';
import '@testing-library/jest-dom';

describe('reasoningAccessibilityContract', () => {
  it('enforces structural accessibility for dynamic AI outputs', async () => {
    const { container, getByRole } = render(
      <div role="status" aria-live="polite" aria-atomic="true">
        AI Reasoning update
      </div>
    );
    
    expect(getByRole('status')).toBeInTheDocument();
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('enforces structural accessibility for evidence hierarchies', async () => {
    const { container } = render(
      <ul role="tree">
        <li role="treeitem" aria-expanded="true">Evidence Parent
          <ul role="group">
            <li role="treeitem">Evidence Child</li>
          </ul>
        </li>
      </ul>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('enforces structural accessibility for confidence metrics', async () => {
    const { container, getByRole } = render(
      <div role="progressbar" aria-label="Confidence score" aria-valuenow={85} aria-valuemin={0} aria-valuemax={100}>
        Confidence: 85%
      </div>
    );
    
    expect(getByRole('progressbar')).toHaveAttribute('aria-valuenow', '85');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
