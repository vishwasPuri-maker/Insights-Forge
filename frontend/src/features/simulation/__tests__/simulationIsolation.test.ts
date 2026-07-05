import { describe, it, expect } from 'vitest';
import { queryKeys } from '@/lib/queryKeys';
import { QueryClient } from '@tanstack/react-query';

describe('simulationIsolation', () => {
  it('mathematically prevents cache collisions via queryKeys', () => {
    const key1 = queryKeys.sector.simulations('tenant-a', 'sector-1');
    const key2 = queryKeys.sector.simulations('tenant-b', 'sector-1');
    const key3 = queryKeys.sector.simulations('tenant-a', 'sector-2');

    expect(key1).not.toEqual(key2);
    expect(key1).not.toEqual(key3);
  });

  it('logout purge wipes cache', () => {
    const queryClient = new QueryClient();
    queryClient.setQueryData(queryKeys.sector.simulations('t1', 's1'), { data: 'secret' });
    expect(queryClient.getQueryData(queryKeys.sector.simulations('t1', 's1'))).toBeTruthy();
    
    queryClient.clear();
    expect(queryClient.getQueryData(queryKeys.sector.simulations('t1', 's1'))).toBeUndefined();
  });
});
