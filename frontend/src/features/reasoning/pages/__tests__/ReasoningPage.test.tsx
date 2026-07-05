import { describe, it, expect, vi } from 'vitest';

import { render, waitFor, screen } from '@/utils/test-utils';
import { ReasoningPage } from '../ReasoningPage';
import { useReasoning } from '../../hooks/useReasoning';
import { useTenantStore } from '@/store/tenantStore';

vi.mock('../../hooks/useReasoning', () => ({
  useReasoning: vi.fn(),
}));

vi.mock('@/store/tenantStore', () => ({
  useTenantStore: vi.fn(),
}));

describe('ReasoningPage', () => {
  const mockData = {
    summary: { topic: 'Topic', executiveSummary: 'Exec', primaryConclusion: 'Conc' },
    insights: [{ id: 'i1', title: 'I1', description: 'D1', severity: 'critical', category: 'anomaly' }],
    factors: [{ id: 'f1', name: 'F1', contributionWeight: 0.5, trend: 'stable' }],
    evidenceNodes: [{ id: 'e1', source: 'S1', description: 'D1', reliability: 0.8 }],
    evidenceEdges: [],
    recommendations: [{ id: 'r1', title: 'R1', description: 'D1', impactScore: 0.9, effortLevel: 'low', actionType: 'optimize' }],
    confidence: { overallScore: 0.85, dataQualityScore: 0.9, modelCertainty: 0.8 }
  };

  it('renders empty state when no tenant context', () => {
    vi.mocked(useTenantStore).mockReturnValue({ tenantId: null, sectorId: null } as unknown as ReturnType<typeof useTenantStore>);
    vi.mocked(useReasoning).mockReturnValue({ isLoading: true } as unknown as ReturnType<typeof useReasoning>);
    render(<ReasoningPage />);
    expect(screen.getByText('No Active Context')).toBeInTheDocument();
  });

  it('renders loading state', () => {
    vi.mocked(useTenantStore).mockReturnValue({ tenantId: 't1', sectorId: 's1' } as unknown as ReturnType<typeof useTenantStore>);
    vi.mocked(useReasoning).mockReturnValue({ isLoading: true } as unknown as ReturnType<typeof useReasoning>);
    render(<ReasoningPage />);
    expect(screen.getByText('Analyzing Evidence')).toBeInTheDocument();
  });

  it('renders error state', () => {
    vi.mocked(useTenantStore).mockReturnValue({ tenantId: 't1', sectorId: 's1' } as unknown as ReturnType<typeof useTenantStore>);
    vi.mocked(useReasoning).mockReturnValue({ isError: true, data: null } as unknown as ReturnType<typeof useReasoning>);
    render(<ReasoningPage />);
    expect(screen.getByText('Reasoning Engine Failure')).toBeInTheDocument();
  });

  it('renders reasoning content on success', async () => {
    vi.mocked(useTenantStore).mockReturnValue({ tenantId: 't1', sectorId: 's1' } as unknown as ReturnType<typeof useTenantStore>);
    vi.mocked(useReasoning).mockReturnValue({ data: mockData, isLoading: false, isError: false } as unknown as ReturnType<typeof useReasoning>);
    
    render(<ReasoningPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Topic')).toBeInTheDocument();
      expect(screen.getByText('I1')).toBeInTheDocument();
      expect(screen.getByText('F1')).toBeInTheDocument();
      expect(screen.getByText('S1')).toBeInTheDocument();
      expect(screen.getByText('R1')).toBeInTheDocument();
    });
  });
});
