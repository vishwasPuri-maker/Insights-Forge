import { describe, it, expect } from 'vitest';
import { authService } from '../authService';
import { useAuthStore } from '@/store/authStore';
import { useTenantStore } from '@/store/tenantStore';
import { useUIStore } from '@/store/uiStore';
import { QueryClient } from '@tanstack/react-query';
import type { UserRole } from '@/types/auth';

describe('logoutIsolation', () => {
  it('destroys all store states and caches on logout', () => {
    // 1. Setup mock states
    useAuthStore.setState({ isAuthenticated: true, token: 'mock-token', role: 'Global Executive' as UserRole });
    useTenantStore.setState({ tenantId: 't-1', sectorId: 's-1' });
    useUIStore.setState({ isIntelligencePanelOpen: true });
    
    const queryClient = new QueryClient();
    queryClient.setQueryData(['mock-key'], { data: 'mock-data' });
    
    // Setup local/session storage
    sessionStorage.setItem('insight-auth-storage', 'mock');
    localStorage.setItem('insight-tenant-storage', 'mock');
    localStorage.setItem('insight-ui-storage', 'mock');

    // 2. Perform global orchestration
    authService.logout(queryClient);

    // 3. Verify pure states reset
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().token).toBeNull();
    expect(useTenantStore.getState().tenantId).toBeNull();
    expect(useTenantStore.getState().sectorId).toBeNull();
    expect(useUIStore.getState().isIntelligencePanelOpen).toBe(false);

    // 4. Verify physical storage nuked
    expect(sessionStorage.getItem('insight-auth-storage')).toBeNull();
    expect(localStorage.getItem('insight-tenant-storage')).toBeNull();
    expect(localStorage.getItem('insight-ui-storage')).toBeNull();

    // 5. Verify query cache nuked
    expect(queryClient.getQueryData(['mock-key'])).toBeUndefined();
  });
});
