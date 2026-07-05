import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
  isSidebarExpanded: boolean;
  isIntelligencePanelOpen: boolean;
  toggleSidebar: () => void;
  toggleIntelligencePanel: () => void;
  setIntelligencePanelOpen: (isOpen: boolean) => void;
  reset: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      isSidebarExpanded: true,
      isIntelligencePanelOpen: false,
      toggleSidebar: () => set((state) => ({ isSidebarExpanded: !state.isSidebarExpanded })),
      toggleIntelligencePanel: () => set((state) => ({ isIntelligencePanelOpen: !state.isIntelligencePanelOpen })),
      setIntelligencePanelOpen: (isOpen) => set({ isIntelligencePanelOpen: isOpen }),
      reset: () => set({ isSidebarExpanded: true, isIntelligencePanelOpen: false }),
    }),
    {
      name: 'insight-ui-storage',
    }
  )
)
