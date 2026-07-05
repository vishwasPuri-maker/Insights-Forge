import { describe, it, expect, vi, beforeEach } from 'vitest';
import { recommendationClient } from '../recommendationClient';
import { apiClient } from '@/services/apiClient';

vi.mock('@/services/apiClient');

describe('recommendationClient', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calls correct API endpoint', async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({ data: { id: 'mock' } });
    await recommendationClient.getAnalysis('t1', 's1');
    expect(apiClient.get).toHaveBeenCalledWith('/tenants/t1/sectors/s1/recommendation');
  });

  it('passes error correctly', async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error('Network error'));
    await expect(recommendationClient.getAnalysis('t1', 's1')).rejects.toThrow('Network error');
  });
});
