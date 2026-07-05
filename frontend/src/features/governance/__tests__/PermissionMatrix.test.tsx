import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { PermissionMatrix } from '../components/PermissionMatrix';
import { usePermissions } from '../hooks/usePermissions';

vi.mock('../hooks/usePermissions');

describe('PermissionMatrix', () => {
  it('renders a grid with row/column structure', () => {
    vi.mocked(usePermissions).mockReturnValue({
      data: [
        { id: 'p1', resource: 'Users', action: 'read', roleId: 'r1' }
      ],
      isLoading: false,
      isError: false,
    } as any);

    const { getByRole, getAllByRole } = render(
      <PermissionMatrix tenantId="t1" role="Admin" />
    );

    expect(getByRole('grid')).toBeInTheDocument();
    expect(getAllByRole('row').length).toBe(2);
  });
});
