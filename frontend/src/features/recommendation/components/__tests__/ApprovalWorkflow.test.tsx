import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ApprovalWorkflowComponent } from '../ApprovalWorkflow';
import type { ApprovalWorkflow } from '@/types/recommendation';

describe('ApprovalWorkflow', () => {
  const mockWorkflow: ApprovalWorkflow = {
    id: 'w1',
    finalStatus: 'pending',
    steps: [
      { id: 's1', role: 'CFO', status: 'approved' },
      { id: 's2', role: 'CEO', status: 'required' }
    ]
  };

  it('renders final status and all steps', () => {
    const { getByText } = render(<ApprovalWorkflowComponent workflow={mockWorkflow} />);
    
    expect(getByText('pending')).toBeInTheDocument();
    expect(getByText('CFO')).toBeInTheDocument();
    expect(getByText('approved')).toBeInTheDocument();
    expect(getByText('CEO')).toBeInTheDocument();
    expect(getByText('required')).toBeInTheDocument();
  });
});
