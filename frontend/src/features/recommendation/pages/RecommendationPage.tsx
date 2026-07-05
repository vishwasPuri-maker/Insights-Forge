import React from 'react';
import { useParams } from 'react-router-dom';
import { OSLayout } from '@/components/layout/OSLayout';
import { OSSection } from '@/components/layout/OSSection';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useRecommendation } from '../hooks/useRecommendation';
import type { ExecutiveRecommendation } from '@/types/recommendation';

const priorityVariant = (priority: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
  if (priority === 'high') return 'destructive';
  if (priority === 'medium') return 'secondary';
  return 'outline';
};

export const RecommendationPage: React.FC = () => {
  const { tenant_id = '', sector_id = '' } = useParams<{ tenant_id: string; sector_id: string }>();
  const { data, isLoading, isError, error } = useRecommendation(tenant_id, sector_id);

  if (isLoading) {
    return (
      <OSLayout
        title="Executive Recommendations"
        description="AI-synthesized strategic recommendations for your sector"
      >
        <div
          className="animate-pulse text-muted-foreground flex items-center gap-2"
          aria-busy="true"
          aria-live="polite"
        >
          <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          Synthesizing Executive Recommendations…
        </div>
      </OSLayout>
    );
  }

  if (isError) {
    return (
      <OSLayout
        title="Executive Recommendations"
        description="AI-synthesized strategic recommendations for your sector"
      >
        <div
          className="p-8 text-brand-error bg-brand-error/5 border border-brand-error/20 rounded-lg"
          role="alert"
        >
          <h2 className="text-h2 font-bold mb-2">Analysis Failed</h2>
          <p>{(error as { message?: string })?.message || 'Please try again.'}</p>
        </div>
      </OSLayout>
    );
  }

  return (
    <OSLayout
      title="Executive Recommendations"
      description="AI-synthesized strategic recommendations for your sector"
    >
      {data?.summary && (
        <OSSection
          title="Executive Summary"
          description={data.summary.topic}
        >
          <p className="text-body text-muted-foreground">{data.summary.executiveSummary}</p>
          <p className="mt-2 text-sm font-medium">{data.summary.primaryConclusion}</p>
        </OSSection>
      )}

      <OSSection
        title="Executive Recommendations"
        description="Strategic actions ranked by impact and priority"
      >
        {!data?.recommendations?.length ? (
          <div className="p-8 text-center text-muted-foreground border border-border rounded-lg">
            No recommendations available for this sector yet.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {data.recommendations.map((rec: ExecutiveRecommendation) => (
              <Card key={rec.id} className="flex flex-col">
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <CardTitle className="text-h4">{rec.title}</CardTitle>
                    <Badge variant={priorityVariant(rec.priority)}>{rec.priority}</Badge>
                  </div>
                </CardHeader>
                <CardContent className="flex-1 space-y-2">
                  <p className="text-body text-muted-foreground">{rec.description}</p>
                  <div className="flex gap-4 text-sm">
                    <span>Impact: {(rec.impactScore * 100).toFixed(0)}%</span>
                    <span>Risk: {(rec.riskScore * 100).toFixed(0)}%</span>
                  </div>
                  {rec.roi && (
                    <p className="text-sm text-muted-foreground">
                      ROI: ${rec.roi.projectedValue.toLocaleString()} in {rec.roi.paybackPeriodDays}d
                    </p>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </OSSection>
    </OSLayout>
  );
};
