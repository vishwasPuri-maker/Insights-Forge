import { useQuery } from '@tanstack/react-query';
import { queryKeys } from '@/lib/queryKeys';
import { simulationClient } from '../api/simulationClient';
import { mapSimulationAnalysis } from '../api/simulationMapper';
import type { SimulationAnalysis, SimulationAnalysisDTO } from '@/types/simulation';

export const useSimulation = (tenantId: string | null, sectorId: string | null) => {
  return useQuery<SimulationAnalysisDTO, Error, SimulationAnalysis>({
    queryKey: queryKeys.sector.simulations(tenantId || '', sectorId || ''),
    queryFn: () => simulationClient.getSimulationAnalysis(tenantId || '', sectorId || ''),
    enabled: Boolean(tenantId && sectorId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
    retry: 1,
    select: mapSimulationAnalysis
  });
};
