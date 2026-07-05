import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { useTenantStore } from '@/store/tenantStore';
import type { UserRole } from '@/types/auth';

interface AuthGuardProps {
  children: React.ReactNode;
  allowedRoles?: UserRole[];
  requireTenant?: boolean;
  requireSector?: boolean;
}

export const AuthGuard: React.FC<AuthGuardProps> = ({ children, allowedRoles, requireTenant, requireSector }) => {
  const { isAuthenticated, role } = useAuthStore();
  const { tenantId, sectorId } = useTenantStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/401" replace />;
  }
  
  if (allowedRoles && role && !allowedRoles.includes(role)) {
    return <Navigate to="/403" replace />;
  }

  if (requireTenant && !tenantId) {
    return <Navigate to="/403" replace />;
  }

  if (requireSector && !sectorId) {
    return <Navigate to="/403" replace />;
  }
  
  return <>{children}</>;
};
