// DTO Models (Backend Wire Format)

export interface GovernanceTenantDTO {
  id: string;
  name: string;
  status: string;
  created_at: string;
}

export interface GovernanceSectorDTO {
  id: string;
  name: string;
  organization_id: string;
  active: boolean;
}

export interface GovernanceRoleDTO {
  id: string;
  name: string;
  level: number;
}

export interface GovernancePermissionDTO {
  id: string;
  resource: string;
  action: string;
  role_id: string;
}

export interface GovernanceUserDTO {
  id: string;
  email: string;
  role: GovernanceRoleDTO;
  organization_id: string;
  last_login: string;
  status: string;
}

export interface GovernanceAuditEntryDTO {
  id: string;
  timestamp: string;
  user_id: string;
  action: string;
  resource: string;
  metadata: Record<string, any>;
  ip_address: string;
}

export interface GovernancePolicyDTO {
  id: string;
  name: string;
  description: string;
  enforced: boolean;
  severity: string;
}

export interface GovernanceAlertDTO {
  id: string;
  type: string;
  message: string;
  timestamp: string;
  severity: string;
  resolved: boolean;
}

export interface GovernanceHealthMetricDTO {
  id: string;
  metric_name: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface GovernanceApprovalDTO {
  id: string;
  resource_id: string;
  status: string;
  requested_by: string;
  approved_by: string | null;
  timestamp: string;
}

export interface GovernanceSummaryDTO {
  active_users: number;
  open_alerts: number;
  pending_approvals: number;
  system_health_score: number;
}

export interface GovernanceAnalysisDTO {
  id: string;
  organization_id: string;
  summary: GovernanceSummaryDTO;
  recent_audits: GovernanceAuditEntryDTO[];
  active_policies: GovernancePolicyDTO[];
  critical_alerts: GovernanceAlertDTO[];
  health_metrics: GovernanceHealthMetricDTO[];
}


// Domain Models (Frontend Consumption)

export interface GovernanceTenant {
  id: string;
  name: string;
  status: string;
  createdAt: string;
}

export interface GovernanceSector {
  id: string;
  name: string;
  tenantId: string;
  active: boolean;
}

export interface GovernanceRole {
  id: string;
  name: string;
  level: number;
}

export interface GovernancePermission {
  id: string;
  resource: string;
  action: string;
  roleId: string;
}

export interface GovernanceUser {
  id: string;
  email: string;
  role: GovernanceRole;
  tenantId: string;
  lastLogin: string;
  status: string;
}

export interface GovernanceAuditEntry {
  id: string;
  timestamp: string;
  userId: string;
  action: string;
  resource: string;
  metadata: Record<string, any>;
  ipAddress: string;
}

export interface GovernancePolicy {
  id: string;
  name: string;
  description: string;
  enforced: boolean;
  severity: string;
}

export interface GovernanceAlert {
  id: string;
  type: string;
  message: string;
  timestamp: string;
  severity: string;
  resolved: boolean;
}

export interface GovernanceHealthMetric {
  id: string;
  metricName: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface GovernanceApproval {
  id: string;
  resourceId: string;
  status: string;
  requestedBy: string;
  approvedBy: string | null;
  timestamp: string;
}

export interface GovernanceSummary {
  activeUsers: number;
  openAlerts: number;
  pendingApprovals: number;
  systemHealthScore: number;
}

export interface GovernanceAnalysis {
  id: string;
  tenantId: string;
  summary: GovernanceSummary;
  recentAudits: GovernanceAuditEntry[];
  activePolicies: GovernancePolicy[];
  criticalAlerts: GovernanceAlert[];
  healthMetrics: GovernanceHealthMetric[];
}
