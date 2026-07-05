import { render } from '@/utils/test-utils';
import { axe } from 'jest-axe';
import { describe, it, expect } from 'vitest';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';

describe('Foundation Components (T3 & T6)', () => {
  it('Button renders correctly and has no a11y violations', async () => {
    const { container, getByRole } = render(<Button>Test Button</Button>);
    expect(getByRole('button')).toHaveTextContent('Test Button');
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Badge renders correctly and has no a11y violations', async () => {
    const { container, getByText } = render(<Badge>Status</Badge>);
    expect(getByText('Status')).toBeInTheDocument();
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Input renders correctly and has no a11y violations', async () => {
    const { container, getByRole } = render(
      <label>
        Username
        <Input placeholder="Enter username" />
      </label>
    );
    expect(getByRole('textbox')).toBeInTheDocument();
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
