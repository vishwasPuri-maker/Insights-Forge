import React from 'react';
import { OSLayout } from '@/components/layout/OSLayout';
import { Card } from '@/components/ui/card';
import { AlertTriangle } from 'lucide-react';

export const ReasoningErrorState: React.FC = () => {
  return (
    <OSLayout title="AI Reasoning OS" description="Analysis unavailable">
      <div className="flex items-center justify-center min-h-[400px]">
        <Card className="p-8 text-center bg-brand-error/10 border-brand-error/20 w-full max-w-md">
          <AlertTriangle className="mx-auto h-12 w-12 text-brand-error mb-4" />
          <div className="text-h3 font-semibold text-brand-error mb-2">Reasoning Engine Failure</div>
          <div className="text-brand-error/80 text-body">
            Unable to retrieve causal patterns for the current sector. Please try again later.
          </div>
        </Card>
      </div>
    </OSLayout>
  );
};
