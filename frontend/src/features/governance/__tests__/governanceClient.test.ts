import { describe, it, expect, vi } from 'vitest';
import { governanceClient } from '../api/governanceClient';
import { apiClient } from '@/services/apiClient';

vi.mock('@/services/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
  }
}));

describe('governanceClient', () => {
  it('throws on missing tenantId or role for analysis', async () => {
    await expect(governanceClient.getGovernanceAnalysis('', '')).rejects.toThrow('Missing boundary context');
  });

  it('throws if response tenant_id mismatches', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: { tenant_id: 't2' } });
    await expect(governanceClient.getGovernanceAnalysis('t1', 'Admin')).rejects.toThrow('Tenant isolation boundary violated: Response tenant_id mismatch');
  });

  it('returns valid analysis payload', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: { tenant_id: 't1', summary: {} } });
    const res = await governanceClient.getGovernanceAnalysis('t1', 'Admin');
    expect(res.tenant_id).toBe('t1');
  });

  it('throws on missing tenantId for users', async () => {
    await expect(governanceClient.getUsers('', 'Admin', 's1')).rejects.toThrow('Missing tenantId');
  });

  it('throws if any user tenant_id mismatches', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: [{ tenant_id: 't2' }] });
    await expect(governanceClient.getUsers('t1', 'Admin', 's1')).rejects.toThrow('Tenant isolation boundary violated: User tenant_id mismatch');
  });
});
