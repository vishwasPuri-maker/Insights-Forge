import { http, HttpResponse } from 'msw';
import type { 
  GovernanceAnalysisDTO,
  GovernanceUserDTO
} from '@/types/governance';

// Mock Data
const mockGovernanceAnalysis: GovernanceAnalysisDTO = {
  id: 'gov_1',
  tenant_id: 't1',
  summary: {
    active_users: 120,
    open_alerts: 3,
    pending_approvals: 5,
    system_health_score: 98,
  },
  recent_audits: [],
  active_policies: [],
  critical_alerts: [],
  health_metrics: [],
};

export const governanceHandlers = [
  http.get('/api/v1/admin/:tenantId/analysis', ({ request, params }) => {
    const { tenantId } = params;
    const url = new URL(request.url);
    const role = url.searchParams.get('role');

    if (tenantId !== 't1') return new HttpResponse(null, { status: 403, statusText: 'Forbidden' });
    if (role !== 'Admin') return new HttpResponse(null, { status: 403, statusText: 'Forbidden: Role Escalation' });

    return HttpResponse.json({ ...mockGovernanceAnalysis, tenant_id: tenantId as string });
  }),

  http.get('/api/v1/admin/:tenantId/users', ({ request, params }) => {
    const { tenantId } = params;
    const role = request.headers.get('X-Role');

    if (tenantId !== 't1') return new HttpResponse(null, { status: 403, statusText: 'Forbidden' });
    if (role !== 'Admin') return new HttpResponse(null, { status: 403, statusText: 'Forbidden' });

    const mockUsers: GovernanceUserDTO[] = [
      { id: 'u1', email: 'admin@t1.com', role: { id: 'r1', name: 'Admin', level: 1 }, tenant_id: tenantId as string, last_login: '2026-07-02', status: 'active' }
    ];

    return HttpResponse.json(mockUsers);
  }),

  http.get('/api/v1/admin/:tenantId/audit', ({ request, params }) => {
    const { tenantId } = params;
    const url = new URL(request.url);
    const role = url.searchParams.get('role');

    if (tenantId !== 't1') return new HttpResponse(null, { status: 403, statusText: 'Forbidden' });
    if (role !== 'Admin') return new HttpResponse(null, { status: 403, statusText: 'Forbidden' });

    return HttpResponse.json([]);
  }),

  http.get('/api/v1/admin/:tenantId/permissions', ({ request, params }) => {
    const { tenantId } = params;
    const url = new URL(request.url);
    const role = url.searchParams.get('role');

    if (tenantId !== 't1') return new HttpResponse(null, { status: 403, statusText: 'Forbidden' });
    if (role !== 'Admin') return new HttpResponse(null, { status: 403, statusText: 'Forbidden' });

    return HttpResponse.json([]);
  }),

  http.get('/api/v1/admin/:tenantId/policies', ({ params }) => {
    const { tenantId } = params;
    if (tenantId !== 't1') return new HttpResponse(null, { status: 403, statusText: 'Forbidden' });
    return HttpResponse.json([]);
  }),

  http.get('/api/v1/admin/:tenantId/health', ({ params }) => {
    const { tenantId } = params;
    if (tenantId !== 't1') return new HttpResponse(null, { status: 403, statusText: 'Forbidden' });
    return HttpResponse.json([]);
  })
];
