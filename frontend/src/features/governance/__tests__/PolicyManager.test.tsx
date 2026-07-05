import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { PolicyManager } from '../components/PolicyManager';
import type { GovernanceAlert, GovernancePolicy } from '@/types/governance';

describe('PolicyManager', () => {
  it('displays critical alerts prominently', () => {
    const alerts: GovernanceAlert[] = [
      { id: 'a1', type: 'SECURITY', message: 'Unauthorized access attempt', severity: 'critical', timestamp: '2026', resolved: false }
    ];
    const { getByText } = render(
      <PolicyManager policies={[]} criticalAlerts={alerts} />
    );
    expect(getByText('Critical Violations Detected')).toBeInTheDocument();
  });

  it('displays policies with enforcement status', () => {
    const policies: GovernancePolicy[] = [
      { id: 'p1', name: 'Data Residency', description: 'desc', enforced: true, severity: 'high' }
    ];
    const { getByText } = render(
      <PolicyManager policies={policies} criticalAlerts={[]} />
    );
    expect(getByText('Data Residency')).toBeInTheDocument();
    expect(getByText('Enforced')).toBeInTheDocument();
  });
});
