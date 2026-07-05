import React from 'react';
import { AINativeCard } from '@/components/ai/AINativeCard';
import type { ReasoningSummary as DomainSummary } from '@/types/reasoning';

interface ReasoningSummaryProps {
  summary: DomainSummary;
  confidenceScore: number; // 0-100%
}

export const ReasoningSummary: React.FC<ReasoningSummaryProps> = ({ summary, confidenceScore }) => {
  return (
    <AINativeCard 
      title={summary.topic} 
      confidenceScore={confidenceScore} 
      type="Prediction"
      description={summary.executiveSummary}
    >
      <div className="mt-4 p-4 bg-muted rounded-md border border-border">
        <h4 className="text-h4 font-semibold tracking-tight text-foreground mb-2">Primary Conclusion</h4>
        <p className="text-body text-foreground">{summary.primaryConclusion}</p>
      </div>
    </AINativeCard>
  );
};
