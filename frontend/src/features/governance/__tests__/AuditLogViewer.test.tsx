import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { AuditLogViewer } from '../components/AuditLogViewer';
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

describe('AuditLogViewer', () => {
  it('renders a filtered view', () => {
    const { getByPlaceholderText } = render(
      <AuditLogViewer initialAudits={[]} tenantId="t1" role="Admin" />,
      { wrapper }
    );
    expect(getByPlaceholderText(/Filter audit logs.../i)).toBeInTheDocument();
  });
});
