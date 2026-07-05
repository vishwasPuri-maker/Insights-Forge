import { describe, it, expect } from 'vitest';
import { queryKeys } from '../queryKeys';

describe('React Query Isolation (T5)', () => {
  it('validates tenant query separation', () => {
    const tenantA = queryKeys.tenant.details('tenant-a');
    const tenantB = queryKeys.tenant.details('tenant-b');
    
    expect(tenantA).not.toEqual(tenantB);
    expect(tenantA[1]).toBe('tenant-a');
    expect(tenantB[1]).toBe('tenant-b');
  });

  it('validates sector query cache separation', () => {
    const sectorAData = queryKeys.sector.all('t1');
    const sectorADashboard = queryKeys.sector.dashboard('t1', 'sector-a');
    const sectorBDashboard = queryKeys.sector.dashboard('t1', 'sector-b');
    
    expect(sectorADashboard).not.toEqual(sectorBDashboard);
    expect(sectorADashboard).not.toEqual(sectorAData);
    
    expect(sectorADashboard).toEqual(['t1', 'sector-a', 'dashboard']);
    expect(sectorBDashboard).toEqual(['t1', 'sector-b', 'dashboard']);
  });
});
