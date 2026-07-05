import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '../authStore';
import { useTenantStore } from '../tenantStore';
import { useUIStore } from '../uiStore';

describe('Zustand Isolation and Persistence (T4)', () => {
  beforeEach(() => {
    sessionStorage.clear();
    localStorage.clear();
    
    // Reset stores
    useAuthStore.setState({ isAuthenticated: false, role: null, token: null });
    useTenantStore.setState({ tenantId: null, sectorId: null });
    useUIStore.setState({ isSidebarExpanded: true, isIntelligencePanelOpen: false });
  });

  it('validates authStore role switching and sessionStorage persistence', () => {
    useAuthStore.getState().login('mock-token', 'mock-refresh-token', 'admin');
    expect(useAuthStore.getState().isAuthenticated).toBe(true);
    expect(useAuthStore.getState().role).toBe('admin');
    
    // Simulate page reload by reading storage
    const storageState = JSON.parse(sessionStorage.getItem('insight-auth-storage') || '{}');
    expect(storageState.state.token).toBe('mock-token');
    expect(storageState.state.role).toBe('admin');
  });

  it('validates tenantStore isolation and localStorage persistence', () => {
    useTenantStore.getState().setTenant('tenant-a');
    useTenantStore.getState().setSector('sector-1');
    
    expect(useTenantStore.getState().tenantId).toBe('tenant-a');
    expect(useTenantStore.getState().sectorId).toBe('sector-1');
    
    const storageState = JSON.parse(localStorage.getItem('insight-tenant-storage') || '{}');
    expect(storageState.state.tenantId).toBe('tenant-a');
    
    // Tenant Switching
    useTenantStore.getState().setTenant('tenant-b');
    expect(useTenantStore.getState().tenantId).toBe('tenant-b');
  });

  it('validates uiStore persistence', () => {
    useUIStore.getState().toggleSidebar();
    expect(useUIStore.getState().isSidebarExpanded).toBe(false);
    
    const storageState = JSON.parse(localStorage.getItem('insight-ui-storage') || '{}');
    expect(storageState.state.isSidebarExpanded).toBe(false);
  });
});
