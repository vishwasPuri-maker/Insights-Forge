import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface TenantState {
  tenantId: string | null;
  sectorId: string | null;
  setTenant: (tenantId: string) => void;
  setSector: (sectorId: string) => void;
  reset: () => void;
}

export const useTenantStore = create<TenantState>()(
  persist(
    (set) => ({
      tenantId: null,
      sectorId: null,
      setTenant: (tenantId) => set({ tenantId }),
      setSector: (sectorId) => set({ sectorId }),
      reset: () => set({ tenantId: null, sectorId: null }),
    }),
    {
      name: 'insight-tenant-storage',
    }
  )
)
