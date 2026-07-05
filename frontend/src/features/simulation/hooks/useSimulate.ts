import { useMutation } from '@tanstack/react-query';
import { simulateClient } from '../api/simulateClient';
import type { SimulateRequest } from '@/types/simulate';

export function useSimulate() {
  return useMutation({
    mutationFn: (body: SimulateRequest) => simulateClient.run(body),
  });
}
