import { describe, it, expect } from 'vitest';
import { queryKeys } from '@/lib/queryKeys';

describe('reasoningIsolation', () => {
  it('guarantees unique query keys per tenant and sector', () => {
    const keyA = queryKeys.sector.reasoning('tenantA', 'sectorX');
    const keyB = queryKeys.sector.reasoning('tenantB', 'sectorX');
    
    expect(keyA).not.toEqual(keyB);
    expect(keyA[0]).toBe('tenantA');
    expect(keyB[0]).toBe('tenantB');
  });

  it('does not contain hardcoded arrays for reasoning', () => {
    const fnStr = queryKeys.sector.reasoning.toString();
    expect(fnStr).not.toContain("['reasoning']");
    expect(fnStr).toContain('tenantId');
    expect(fnStr).toContain('sectorId');
  });
});
