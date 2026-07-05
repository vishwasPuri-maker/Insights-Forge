import React, { useMemo } from 'react';
import { useUIStore } from '@/store/uiStore';
import { IntelligencePanel } from '@/components/ai/IntelligencePanel';
import { Outlet, NavLink, useParams, useLocation } from 'react-router-dom';
import { LayoutDashboard, Brain, Activity, Lightbulb, ShieldCheck, Menu, ChevronRight, Bot, LogOut } from 'lucide-react';
import { buildOperatingSystemRoute, roleGuard } from '@/utils/routes';
import type { OperatingSystemType } from '@/utils/routes';
import { useAuthStore } from '@/store/authStore';
import { authService } from '@/services/auth/authService';
import { useQueryClient } from '@tanstack/react-query';

const OS_DEFINITIONS: { id: OperatingSystemType; label: string; icon: React.FC<any> }[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'reasoning', label: 'Reasoning', icon: Brain },
  { id: 'simulations', label: 'Simulation', icon: Activity },
  { id: 'recommendation', label: 'Recommendation', icon: Lightbulb },
  { id: 'chat', label: 'AI Assistant', icon: Bot },
  { id: 'governance', label: 'Governance', icon: ShieldCheck },
];

export const ApplicationShell: React.FC = () => {
  const { isSidebarExpanded, toggleSidebar } = useUIStore();
  const { tenant_id, sector_id } = useParams<{ tenant_id: string; sector_id: string }>();
  const { role } = useAuthStore();
  const location = useLocation();
  const queryClient = useQueryClient();

  const activeTenant = tenant_id || 't1';
  const activeSector = sector_id || 'sector1';

  const visibleOperatingSystems = useMemo(() => {
    return OS_DEFINITIONS.filter((os) => roleGuard(role, os.id));
  }, [role]);

  // Derive active OS from path for breadcrumb
  const currentPathSegment = location.pathname.split('/').pop() || '';
  const currentOsLabel = OS_DEFINITIONS.find(
    (os) => os.id === currentPathSegment || (os.id === 'governance' && currentPathSegment === 'admin')
  )?.label || 'Overview';

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      {/* Sidebar */}
      <aside
        className={`transition-all duration-300 border-r bg-card hidden md:flex flex-col ${
          isSidebarExpanded ? 'w-[256px]' : 'w-[72px]'
        }`}
        aria-label="Sidebar Navigation"
      >
        <div className="h-[64px] flex items-center px-4 border-b">
          {isSidebarExpanded ? (
            <span className="font-bold text-foreground truncate">Insight Forge</span>
          ) : (
            <span className="font-bold text-foreground">IF</span>
          )}
        </div>
        <nav className="flex-1 overflow-y-auto py-4 px-2 space-y-1" aria-label="Main Navigation">
          {visibleOperatingSystems.map((os) => {
            const Icon = os.icon;
            const to = buildOperatingSystemRoute(activeTenant, activeSector, os.id);
            return (
              <NavLink
                key={os.id}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2 rounded-md transition-colors outline-none focus:outline-none focus-visible:outline-none ${
                    isActive ? 'bg-white text-neutral-900 font-semibold' : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                  }`
                }
                title={!isSidebarExpanded ? os.label : undefined}
                aria-label={`Navigate to ${os.label} Operating System`}
              >
                <Icon className="w-5 h-5 shrink-0" />
                {isSidebarExpanded && <span className="text-sm font-medium">{os.label}</span>}
              </NavLink>
            );
          })}
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Topbar */}
        <header className="h-[64px] border-b bg-card flex items-center px-4 md:px-6 justify-between shrink-0">
          <div className="flex items-center gap-4">
            <button
              onClick={toggleSidebar}
              className="p-2 -ml-2 rounded-md hover:bg-muted text-muted-foreground hidden md:block focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              aria-label={isSidebarExpanded ? 'Collapse Sidebar' : 'Expand Sidebar'}
            >
              <Menu className="w-5 h-5" />
            </button>
            <nav aria-label="Breadcrumb" className="flex items-center text-sm font-medium text-muted-foreground">
              <span className="hidden sm:inline-block truncate max-w-[150px]">{activeTenant}</span>
              <ChevronRight className="w-4 h-4 mx-1 hidden sm:inline-block" />
              <span className="hidden sm:inline-block truncate max-w-[150px]">{activeSector}</span>
              <ChevronRight className="w-4 h-4 mx-1 hidden sm:inline-block" />
              <span className="text-foreground" aria-current="page">{currentOsLabel}</span>
            </nav>
          </div>
          <button
            onClick={() => authService.logout(queryClient)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-colors focus-visible:outline-none"
            aria-label="Logout"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </header>

        {/* Mobile Navigation (Bottom Bar or Drawer - simplified here for constraints) */}
        <div className="md:hidden border-b bg-card w-full overflow-x-auto">
          <nav className="flex px-2 py-2 gap-2" aria-label="Mobile Navigation">
             {visibleOperatingSystems.map((os) => {
              const Icon = os.icon;
              const to = buildOperatingSystemRoute(activeTenant, activeSector, os.id);
              return (
                <NavLink
                  key={os.id}
                  to={to}
                  className={({ isActive }) =>
                    `flex items-center gap-2 px-3 py-2 rounded-md shrink-0 transition-colors outline-none focus:outline-none focus-visible:outline-none ${
                      isActive ? 'bg-white text-neutral-900 font-semibold' : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    }`
                  }
                  aria-label={`Navigate to ${os.label}`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-xs font-medium">{os.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Workspace */}
        <main className="flex-1 overflow-auto p-4 md:p-8 relative outline-none focus:outline-none focus-visible:outline-none" id="main-content" tabIndex={-1}>
          <Outlet />
        </main>
      </div>

      {/* Intelligence Panel */}
      <div className="hidden lg:block shrink-0">
        <IntelligencePanel />
      </div>
    </div>
  );
};
