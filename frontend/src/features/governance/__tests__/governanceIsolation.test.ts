import { describe, it, expect } from 'vitest';
import { governanceClient } from '../api/governanceClient';

describe('governanceIsolation', () => {
  it('rejects cross-tenant access via MSW boundary', async () => {
    await expect(governanceClient.getGovernanceAnalysis('malicious_tenant', 'Admin')).rejects.toThrow();
  });

  it('rejects cross-tenant users request', async () => {
    await expect(governanceClient.getUsers('t2', 'Admin', 'session123')).rejects.toThrow();
  });
});
