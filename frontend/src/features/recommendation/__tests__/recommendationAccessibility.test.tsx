import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { RecommendationPage } from '../pages/RecommendationPage';
import { useRecommendation } from '../hooks/useRecommendation';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import type { RecommendationAnalysis } from '@/types/recommendation';

expect.extend(toHaveNoViolations);
vi.mock('../hooks/useRecommendation');

describe('recommendationAccessibility', () => {
  const renderWithRouter = (component: React.ReactNode) => {
    return render(
      <MemoryRouter initialEntries={['/t1/s1/recommendation']}>
        <Routes>
          <Route path="/:tenant_id/:sector_id/recommendation" element={component} />
        </Routes>
      </MemoryRouter>
    );
  };

  it('has no accessibility violations in loaded state', async () => {
    const mockData: RecommendationAnalysis = {
      id: 'rec_1',
      tenantId: 't1',
      sectorId: 's1',
      metadata: { generatedAt: 'now', modelId: 'm1', processingTimeMs: 100 },
      confidence: { actionabilityScore: 0.9, dataQualityScore: 0.9, modelCertainty: 0.9 },
      summary: { topic: 'Topic', executiveSummary: 'Sum', primaryConclusion: 'Con' },
      recommendations: [
        {
          id: 'r1',
          title: 'Action',
          description: 'Desc',
          priority: 'high',
          impactScore: 0.8,
          riskScore: 0.3,
          roi: { id: 'roi1', projectedValue: 1000, paybackPeriodDays: 30, confidenceLower: 900, confidenceUpper: 1100 },
          actionPlan: { 
            id: 'ap1', 
            title: 'Plan', 
            totalEstimatedDays: 10, 
            steps: [{ id: 's1', description: 'Step', owner: 'Owner', estimatedDays: 5, dependencies: [] }] 
          },
          approval: { 
            id: 'app1', 
            finalStatus: 'pending', 
            steps: [{ id: 'as1', role: 'CFO', status: 'required' }] 
          }
        }
      ]
    };

    vi.mocked(useRecommendation).mockReturnValue({
      isLoading: false,
      isError: false,
      data: mockData,
      error: null,
    } as any);

    const { container } = renderWithRouter(<RecommendationPage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
