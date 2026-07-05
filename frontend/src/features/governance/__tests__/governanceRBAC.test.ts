import { describe, it, expect } from 'vitest';
import { governanceClient } from '../api/governanceClient';

describe('governanceRBAC', () => {
  it('rejects access for Manager role', async () => {
    await expect(governanceClient.getGovernanceAnalysis('t1', 'Manager')).rejects.toThrow();
  });

  it('rejects access for User role in users request', async () => {
    await expect(governanceClient.getUsers('t1', 'User', 'sess1')).rejects.toThrow();
  });

  it('rejects access if role is missing', async () => {
    await expect(governanceClient.getGovernanceAnalysis('t1', '')).rejects.toThrow();
  });
});
