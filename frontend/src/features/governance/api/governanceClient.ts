import type {
  GovernanceAnalysisDTO,
  GovernanceUserDTO,
  GovernanceAuditEntryDTO,
  GovernancePermissionDTO,
  GovernancePolicyDTO,
  GovernanceHealthMetricDTO
} from '@/types/governance';
import type { ApiErrorResponse } from '@/types/api';

// NOTE: The backend contract (openapi.json) exposes GET/POST/DELETE /users and
// GET/PUT /thresholds, but NONE of the aggregated /admin/{tenant}/* governance
// endpoints this feature was built against (analysis, users, audit, permissions,
// policies, health) — and their response shapes differ from the contract's
// UserOut. Until matching endpoints exist, every governance call fails
// gracefully so the Governance screen renders its error/empty state instead of
// hitting nonexistent paths.
const notAvailable = (surface: string): Promise<never> => {
  const error: ApiErrorResponse = {
    code: 'ENDPOINT_NOT_AVAILABLE',
    message: `Governance ${surface} is not available in the current backend.`,
    details: {},
    timestamp: new Date().toISOString(),
  };
  return Promise.reject(error);
};

export const governanceClient = {
  getGovernanceAnalysis: async (
    _tenantId: string,
    _role: string,
  ): Promise<GovernanceAnalysisDTO> => notAvailable('analysis'),

  getUsers: async (
    _tenantId: string,
    _role: string,
    _sessionId: string,
  ): Promise<GovernanceUserDTO[]> => notAvailable('user directory'),

  getAuditLogs: async (
    _tenantId: string,
    _role: string,
    _filters: string,
  ): Promise<GovernanceAuditEntryDTO[]> => notAvailable('audit log'),

  getPermissions: async (
    _tenantId: string,
    _role: string,
  ): Promise<GovernancePermissionDTO[]> => notAvailable('permission matrix'),

  getPolicies: async (_tenantId: string): Promise<GovernancePolicyDTO[]> =>
    notAvailable('policies'),

  getHealth: async (_tenantId: string): Promise<GovernanceHealthMetricDTO[]> =>
    notAvailable('system health'),
};
