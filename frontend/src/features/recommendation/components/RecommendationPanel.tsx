import React from 'react';
import type { ExecutiveRecommendation } from '@/types/recommendation';
import { RecommendationCard } from './RecommendationCard';

interface RecommendationPanelProps {
  recommendations: ExecutiveRecommendation[];
}

export const RecommendationPanel: React.FC<RecommendationPanelProps> = ({ recommendations }) => {
  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="p-8 text-center text-muted-foreground border border-dashed border-border rounded-lg">
        No executive recommendations available for this scenario.
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-8" role="region" aria-label="Executive Recommendations">
      {recommendations.map((rec) => (
        <RecommendationCard key={rec.id} recommendation={rec} />
      ))}
    </div>
  );
};
