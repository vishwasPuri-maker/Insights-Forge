import { describe, it, expect } from 'vitest';
import { reasoningClient } from '../api/reasoningClient';

describe('reasoningClient', () => {
  it('fetches reasoning analysis successfully', async () => {
    const data = await reasoningClient.getReasoningAnalysis('t-mock', 's1');
    expect(data.id).toBe('ra-1');
    expect(data.tenant_id).toBe('t-mock');
    expect(data.sector_id).toBe('s1');
    expect(data.insights.length).toBeGreaterThan(0);
  });

  it('enforces tenant isolation checking', async () => {
    await expect(
      reasoningClient.getReasoningAnalysis('wrong-tenant', 's1')
    ).rejects.toThrow('Tenant isolation violation detected in response payload');
  });
});
