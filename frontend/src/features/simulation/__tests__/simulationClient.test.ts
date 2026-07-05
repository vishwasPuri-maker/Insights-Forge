import { describe, it, expect } from 'vitest';
import { simulationClient } from '../api/simulationClient';
import { server } from '@/mocks/server';
import { http, HttpResponse } from 'msw';

const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

describe('simulationClient', () => {
  it('throws error if tenantId or sectorId is missing', async () => {
    await expect(simulationClient.getSimulationAnalysis('', 's1')).rejects.toThrow('Tenant ID and Sector ID are required');
  });

  it('throws error if tenant isolation boundary is violated', async () => {
    server.use(
      http.get(`${API_URL}/sectors/:sectorId/simulations`, () => {
        return HttpResponse.json({ tenant_id: 'wrong', sector_id: 's1' });
      })
    );
    await expect(simulationClient.getSimulationAnalysis('t1', 's1')).rejects.toThrow('Tenant isolation boundary violation');
  });

  it('throws error if sector isolation boundary is violated', async () => {
    server.use(
      http.get(`${API_URL}/sectors/:sectorId/simulations`, () => {
        return HttpResponse.json({ tenant_id: 't1', sector_id: 'wrong' });
      })
    );
    await expect(simulationClient.getSimulationAnalysis('t1', 's1')).rejects.toThrow('Sector isolation boundary violation');
  });

  it('returns data on successful isolation check', async () => {
    const mockData = { tenant_id: 't1', sector_id: 's1', status: 'success' };
    server.use(
      http.get(`${API_URL}/sectors/:sectorId/simulations`, () => {
        return HttpResponse.json(mockData);
      })
    );
    const result = await simulationClient.getSimulationAnalysis('t1', 's1');
    expect(result.tenant_id).toEqual('t1');
  });
});
