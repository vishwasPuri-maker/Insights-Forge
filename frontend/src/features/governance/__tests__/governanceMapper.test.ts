import { describe, it, expect } from 'vitest';
import { 
  mapGovernanceAnalysis,
  mapGovernanceUser,
  mapGovernancePermission,
  mapGovernanceApproval,
  mapGovernanceTenant,
  mapGovernanceSector
} from '../api/governanceMapper';

describe('governanceMapper', () => {
  it('maps GovernanceAnalysisDTO to GovernanceAnalysis purely', () => {
    const dto = {
      id: 'g1',
      tenant_id: 't1',
      summary: {
        active_users: 10,
        open_alerts: 2,
        pending_approvals: 3,
        system_health_score: 100
      },
      recent_audits: [{ id: 'a1', timestamp: '2026', user_id: 'u1', action: 'login', resource: 'auth', metadata: {}, ip_address: '1.1.1.1' }],
      active_policies: [{ id: 'p1', name: 'Pol', description: 'Desc', enforced: true, severity: 'high' }],
      critical_alerts: [{ id: 'al1', type: 'sec', message: 'msg', timestamp: '2026', severity: 'high', resolved: false }],
      health_metrics: [{ id: 'h1', metric_name: 'cpu', value: 50, unit: '%', timestamp: '2026' }]
    };

    const domain = mapGovernanceAnalysis(dto);

    expect(domain.tenantId).toBe('t1');
    expect(domain.summary.activeUsers).toBe(10);
    expect(domain.recentAudits[0].userId).toBe('u1');
    expect(domain.activePolicies[0].name).toBe('Pol');
    expect(domain.criticalAlerts[0].type).toBe('sec');
    expect(domain.healthMetrics[0].metricName).toBe('cpu');
  });

  it('maps User DTO to Domain', () => {
    const dto = { id: 'u1', email: 'a@b.c', role: { id: 'r1', name: 'Admin', level: 1 }, tenant_id: 't1', last_login: 'now', status: 'active' };
    const domain = mapGovernanceUser(dto);
    expect(domain.tenantId).toBe('t1');
    expect(domain.lastLogin).toBe('now');
  });

  it('maps Permission DTO to Domain', () => {
    const dto = { id: 'p1', resource: 'sys', action: 'read', role_id: 'r1' };
    const domain = mapGovernancePermission(dto);
    expect(domain.roleId).toBe('r1');
  });

  it('maps Approval DTO to Domain', () => {
    const dto = { id: 'a1', resource_id: 'r1', status: 'ok', requested_by: 'u1', approved_by: null, timestamp: 'now' };
    const domain = mapGovernanceApproval(dto);
    expect(domain.resourceId).toBe('r1');
    expect(domain.requestedBy).toBe('u1');
  });

  it('maps Tenant DTO to Domain', () => {
    const dto = { id: 't1', name: 'Acme', status: 'active', created_at: 'now' };
    const domain = mapGovernanceTenant(dto);
    expect(domain.createdAt).toBe('now');
  });

  it('maps Sector DTO to Domain', () => {
    const dto = { id: 's1', name: 'Retail', tenant_id: 't1', active: true };
    const domain = mapGovernanceSector(dto);
    expect(domain.tenantId).toBe('t1');
  });
});
