import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/react';
import { ExecutiveOverride } from '../components/ExecutiveOverride';

describe('ExecutiveOverride', () => {
  const mockApproval = {
    id: 'app1',
    resourceId: 'res1',
    status: 'pending',
    requestedBy: 'user1',
    approvedBy: null,
    timestamp: '2026-07-01T00:00:00Z',
  };

  it('is a pure presentation component calling correct props', () => {
    const onApprove = vi.fn();
    const onReject = vi.fn();
    const onEscalate = vi.fn();
    const onEmergencyOverride = vi.fn();
    const onClose = vi.fn();

    const { getByText } = render(
      <ExecutiveOverride 
        approval={mockApproval}
        onApprove={onApprove}
        onReject={onReject}
        onEscalate={onEscalate}
        onEmergencyOverride={onEmergencyOverride}
        onClose={onClose}
      />
    );

    fireEvent.click(getByText('Approve'));
    expect(onApprove).toHaveBeenCalledWith('app1');

    fireEvent.click(getByText('Cancel'));
    expect(onClose).toHaveBeenCalled();
  });
});
