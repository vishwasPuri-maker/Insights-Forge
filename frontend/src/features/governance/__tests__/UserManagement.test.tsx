import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { UserManagement } from '../components/UserManagement';
import { useUsers } from '../hooks/useUsers';

vi.mock('../hooks/useUsers');

describe('UserManagement', () => {
  it('renders user directory table', () => {
    vi.mocked(useUsers).mockReturnValue({
      data: [
        { id: 'u1', email: 'test@test.com', role: { id: 'r1', name: 'Admin', permissions: [] }, status: 'active', lastLogin: '2026', tenantId: 't1' }
      ],
      isLoading: false,
      isError: false,
    } as any);

    const { getByText } = render(<UserManagement tenantId="t1" role="Admin" sessionId="s1" />);
    expect(getByText('test@test.com')).toBeInTheDocument();
  });
});
