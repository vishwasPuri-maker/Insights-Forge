import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ExecutiveOverride } from '../components/ExecutiveOverride';
import type { GovernanceApproval } from '@/types/governance';

expect.extend(toHaveNoViolations);

describe('GovernanceAccessibility', () => {
  it('ExecutiveOverride meets dialog accessibility contracts', async () => {
    const mockApproval: GovernanceApproval = {
      id: 'app1',
      resourceId: 'res1',
      status: 'pending',
      requestedBy: 'user1',
      approvedBy: null,
      timestamp: '2026-07-01T00:00:00Z',
    };

    const { container, getByRole } = render(
      <ExecutiveOverride 
        approval={mockApproval}
        onApprove={() => {}}
        onReject={() => {}}
        onEscalate={() => {}}
        onEmergencyOverride={() => {}}
        onClose={() => {}}
      />
    );

    const dialog = getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-labelledby', 'override-title');
    expect(dialog).toHaveAttribute('aria-describedby', 'override-desc');
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
