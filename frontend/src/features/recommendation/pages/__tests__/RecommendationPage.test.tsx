import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, waitFor } from '@testing-library/react';
import { RecommendationPage } from '../RecommendationPage';
import { useRecommendation } from '../../hooks/useRecommendation';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import type { RecommendationAnalysis } from '@/types/recommendation';

vi.mock('../../hooks/useRecommendation');

describe('RecommendationPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderWithRouter = (component: React.ReactNode) => {
    return render(
      <MemoryRouter initialEntries={['/t1/s1/recommendation']}>
        <Routes>
          <Route path="/:tenant_id/:sector_id/recommendation" element={component} />
        </Routes>
      </MemoryRouter>
    );
  };

  it('renders loading state', () => {
    vi.mocked(useRecommendation).mockReturnValue({
      isLoading: true,
      isError: false,
      data: undefined,
      error: null,
    } as any);

    const { getAllByText } = renderWithRouter(<RecommendationPage />);
    expect(getAllByText(/Synthesizing Executive Recommendations/i)[0]).toBeInTheDocument();
  });

  it('renders error state', () => {
    vi.mocked(useRecommendation).mockReturnValue({
      isLoading: false,
      isError: true,
      data: undefined,
      error: new Error('Mock error'),
    } as any);

    const { getAllByText } = renderWithRouter(<RecommendationPage />);
    expect(getAllByText(/Analysis Failed/i)[0]).toBeInTheDocument();
  });

  it('renders recommendation data', async () => {
    const mockData: RecommendationAnalysis = {
      id: 'rec_1',
      tenantId: 't1',
      sectorId: 's1',
      metadata: { generatedAt: 'now', modelId: 'm1', processingTimeMs: 100 },
      confidence: { actionabilityScore: 0.9, dataQualityScore: 0.9, modelCertainty: 0.9 },
      summary: { topic: 'Topic A', executiveSummary: 'Exec Sum', primaryConclusion: 'Conc' },
      recommendations: [
        {
          id: 'r1',
          title: 'Action 1',
          description: 'Desc 1',
          priority: 'high',
          impactScore: 0.8,
          riskScore: 0.3,
          roi: { id: 'roi1', projectedValue: 1000, paybackPeriodDays: 30, confidenceLower: 900, confidenceUpper: 1100 },
          actionPlan: { id: 'ap1', title: 'Plan 1', totalEstimatedDays: 10, steps: [] },
          approval: { id: 'app1', finalStatus: 'pending', steps: [] }
        }
      ]
    };

    vi.mocked(useRecommendation).mockReturnValue({
      isLoading: false,
      isError: false,
      data: mockData,
      error: null,
    } as any);

    const { getByText } = renderWithRouter(<RecommendationPage />);
    
    await waitFor(() => {
      expect(getByText('Executive Recommendations')).toBeInTheDocument();
      expect(getByText('Exec Sum')).toBeInTheDocument();
      expect(getByText('Action 1')).toBeInTheDocument();
    });
  });
});
