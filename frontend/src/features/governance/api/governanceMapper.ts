import type {
  GovernanceAnalysis,
  GovernanceAnalysisDTO,
  GovernanceSummary,
  GovernanceSummaryDTO,
  GovernanceUser,
  GovernanceUserDTO,
  GovernanceRole,
  GovernanceRoleDTO,
  GovernancePermission,
  GovernancePermissionDTO,
  GovernanceAuditEntry,
  GovernanceAuditEntryDTO,
  GovernancePolicy,
  GovernancePolicyDTO,
  GovernanceAlert,
  GovernanceAlertDTO,
  GovernanceHealthMetric,
  GovernanceHealthMetricDTO,
  GovernanceApproval,
  GovernanceApprovalDTO,
  GovernanceTenant,
  GovernanceTenantDTO,
  GovernanceSector,
  GovernanceSectorDTO
} from '@/types/governance';

export const mapGovernanceRole = (dto: GovernanceRoleDTO): GovernanceRole => ({
  id: dto.id,
  name: dto.name,
  level: dto.level,
});

export const mapGovernancePermission = (dto: GovernancePermissionDTO): GovernancePermission => ({
  id: dto.id,
  resource: dto.resource,
  action: dto.action,
  roleId: dto.role_id,
});

export const mapGovernanceUser = (dto: GovernanceUserDTO): GovernanceUser => ({
  id: dto.id,
  email: dto.email,
  role: mapGovernanceRole(dto.role),
  tenantId: (dto as unknown as Record<string, unknown>)['tenant_id'] as string ?? dto.organization_id,
  lastLogin: dto.last_login,
  status: dto.status,
});

export const mapGovernanceAuditEntry = (dto: GovernanceAuditEntryDTO): GovernanceAuditEntry => ({
  id: dto.id,
  timestamp: dto.timestamp,
  userId: dto.user_id,
  action: dto.action,
  resource: dto.resource,
  metadata: { ...dto.metadata },
  ipAddress: dto.ip_address,
});

export const mapGovernancePolicy = (dto: GovernancePolicyDTO): GovernancePolicy => ({
  id: dto.id,
  name: dto.name,
  description: dto.description,
  enforced: dto.enforced,
  severity: dto.severity,
});

export const mapGovernanceAlert = (dto: GovernanceAlertDTO): GovernanceAlert => ({
  id: dto.id,
  type: dto.type,
  message: dto.message,
  timestamp: dto.timestamp,
  severity: dto.severity,
  resolved: dto.resolved,
});

export const mapGovernanceHealthMetric = (dto: GovernanceHealthMetricDTO): GovernanceHealthMetric => ({
  id: dto.id,
  metricName: dto.metric_name,
  value: dto.value,
  unit: dto.unit,
  timestamp: dto.timestamp,
});

export const mapGovernanceApproval = (dto: GovernanceApprovalDTO): GovernanceApproval => ({
  id: dto.id,
  resourceId: dto.resource_id,
  status: dto.status,
  requestedBy: dto.requested_by,
  approvedBy: dto.approved_by,
  timestamp: dto.timestamp,
});

export const mapGovernanceTenant = (dto: GovernanceTenantDTO): GovernanceTenant => ({
  id: dto.id,
  name: dto.name,
  status: dto.status,
  createdAt: dto.created_at,
});

export const mapGovernanceSector = (dto: GovernanceSectorDTO): GovernanceSector => ({
  id: dto.id,
  name: dto.name,
  tenantId: (dto as unknown as Record<string, unknown>)['tenant_id'] as string ?? dto.organization_id,
  active: dto.active,
});

export const mapGovernanceSummary = (dto: GovernanceSummaryDTO): GovernanceSummary => ({
  activeUsers: dto.active_users,
  openAlerts: dto.open_alerts,
  pendingApprovals: dto.pending_approvals,
  systemHealthScore: dto.system_health_score,
});

export const mapGovernanceAnalysis = (dto: GovernanceAnalysisDTO): GovernanceAnalysis => ({
  id: dto.id,
  tenantId: (dto as unknown as Record<string, unknown>)['tenant_id'] as string ?? dto.organization_id,
  summary: mapGovernanceSummary(dto.summary),
  recentAudits: dto.recent_audits.map(mapGovernanceAuditEntry),
  activePolicies: dto.active_policies.map(mapGovernancePolicy),
  criticalAlerts: dto.critical_alerts.map(mapGovernanceAlert),
  healthMetrics: dto.health_metrics.map(mapGovernanceHealthMetric),
});
