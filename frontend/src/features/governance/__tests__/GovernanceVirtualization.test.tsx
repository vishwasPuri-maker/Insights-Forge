import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { AuditLogViewer } from '../components/AuditLogViewer';
import type { GovernanceAuditEntry } from '@/types/governance';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

const queryClient = new QueryClient();
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

vi.mock('../hooks/useAudit', () => ({
  useAudit: vi.fn(() => ({ data: undefined, isLoading: false }))
}));

describe('GovernanceVirtualization', () => {
  it('renders standard table when rows < 100', () => {
    const smallDataSet: GovernanceAuditEntry[] = Array.from({ length: 99 }).map((_, i) => ({
      id: `a${i}`, timestamp: '2026', userId: 'u1', action: 'read', resource: 'res', metadata: {}, ipAddress: '1.1.1.1'
    }));

    const { getByRole, getAllByRole } = render(
      <AuditLogViewer initialAudits={smallDataSet} tenantId="t1" role="Admin" />,
      { wrapper }
    );

    // Should render a standard table from ExecutiveTable
    expect(getByRole('table')).toBeInTheDocument();
    // 99 rows + 1 header = 100 rows total rendered in DOM
    const rows = getAllByRole('row');
    expect(rows.length).toBe(100);
  });

  it('virtualizes rendering when rows >= 100', () => {
    const largeDataSet: GovernanceAuditEntry[] = Array.from({ length: 5000 }).map((_, i) => ({
      id: `a${i}`, timestamp: '2026', userId: 'u1', action: 'read', resource: 'res', metadata: {}, ipAddress: '1.1.1.1'
    }));

    const { getByRole, getAllByRole } = render(
      <AuditLogViewer initialAudits={largeDataSet} tenantId="t1" role="Admin" />,
      { wrapper }
    );

    const table = getByRole('table');
    expect(table).toHaveAttribute('aria-rowcount', '5001');

    // Due to virtualization (overscan 5), it should render far fewer than 5000 rows
    const rows = getAllByRole('row');
    expect(rows.length).toBeLessThan(100);
  });
});
