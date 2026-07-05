import React from 'react';
import { AINativeCard } from '@/components/ai/AINativeCard';
import type { Recommendation } from '@/types/dashboard';

interface RecommendationPanelProps {
  recommendations: Recommendation[];
}

export const RecommendationPanel: React.FC<RecommendationPanelProps> = ({ recommendations }) => {
  if (recommendations.length === 0) {
    return <div className="p-4 text-muted-foreground text-center border border-border rounded-lg bg-card">No recommendations available.</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" aria-live="polite" role="status" aria-atomic="true">
      {recommendations.map(rec => (
        <AINativeCard
          key={rec.id}
          title={rec.title}
          confidenceScore={rec.impactScore}
          type="Recommendation"
          description={rec.description}
        >
          <div className="mt-4 pt-4 border-t border-border flex justify-between items-center text-caption text-muted-foreground">
            <span>Effort: <span className="font-medium text-foreground uppercase">{rec.effortLevel}</span></span>
            <span>Action: <span className="font-medium text-foreground uppercase">{rec.actionType}</span></span>
          </div>
        </AINativeCard>
      ))}
    </div>
  );
};
