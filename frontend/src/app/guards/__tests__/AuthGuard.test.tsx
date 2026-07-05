import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AuthGuard } from '../AuthGuard';
import { useAuthStore } from '@/store/authStore';
import { useTenantStore } from '@/store/tenantStore';
import type { UserRole } from '@/types/auth';
import { MemoryRouter, Routes, Route } from 'react-router-dom';

describe('AuthGuard', () => {
  const renderGuard = (allowedRoles?: UserRole[]) => render(
    <MemoryRouter initialEntries={['/protected']}>
      <Routes>
        <Route path="/protected" element={<AuthGuard allowedRoles={allowedRoles}><div>Protected Content</div></AuthGuard>} />
        <Route path="/401" element={<div>401 Unauthorized</div>} />
        <Route path="/403" element={<div>403 Forbidden</div>} />
      </Routes>
    </MemoryRouter>
  );

  it('Case 1: ALLOW when authenticated and role is permitted', () => {
    useAuthStore.setState({ isAuthenticated: true, role: 'Global Executive' as UserRole });
    renderGuard(['Global Executive' as UserRole]);
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('Case 2: REDIRECT to /401 when unauthenticated', () => {
    useAuthStore.setState({ isAuthenticated: false, role: null });
    renderGuard(['Global Executive' as UserRole]);
    expect(screen.getByText('401 Unauthorized')).toBeInTheDocument();
  });

  it('Case 3: REDIRECT to /403 when authenticated but role is unauthorized', () => {
    useAuthStore.setState({ isAuthenticated: true, role: 'Field Operator' as UserRole });
    renderGuard(['Global Executive' as UserRole]);
    expect(screen.getByText('403 Forbidden')).toBeInTheDocument();
  });

  it('Case 4: DENY when wrong tenant (missing tenant)', () => {
    useAuthStore.setState({ isAuthenticated: true, role: 'Global Executive' as UserRole });
    useTenantStore.setState({ tenantId: null });
    
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/protected" element={<AuthGuard requireTenant><div>Protected Content</div></AuthGuard>} />
          <Route path="/403" element={<div>403 Forbidden</div>} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText('403 Forbidden')).toBeInTheDocument();
  });

  it('Case 5: DENY when wrong sector (missing sector)', () => {
    useAuthStore.setState({ isAuthenticated: true, role: 'Global Executive' as UserRole });
    useTenantStore.setState({ tenantId: 't1', sectorId: null });
    
    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/protected" element={<AuthGuard requireSector><div>Protected Content</div></AuthGuard>} />
          <Route path="/403" element={<div>403 Forbidden</div>} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText('403 Forbidden')).toBeInTheDocument();
  });
});
