import { create } from 'zustand'

interface DashboardState {
  activeSectorId: string
  datetimeLowerBound: string
  activeFiltersArray: string[]
  setActiveSector: (sector: string) => void
  setDatetimeBound: (bound: string) => void
  setFilters: (filters: string[]) => void
}

export const useDashboardStore = create<DashboardState>()((set) => ({
  activeSectorId: 'retail',
  datetimeLowerBound: new Date().toISOString(),
  activeFiltersArray: [],
  setActiveSector: (sector) => set({ activeSectorId: sector }),
  setDatetimeBound: (bound) => set({ datetimeLowerBound: bound }),
  setFilters: (filters) => set({ activeFiltersArray: filters }),
}))
