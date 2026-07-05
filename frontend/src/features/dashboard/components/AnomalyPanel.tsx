import React from 'react';
import { AINativeCard } from '@/components/ai/AINativeCard';
import type { Anomaly } from '@/types/dashboard';

interface AnomalyPanelProps {
  anomalies: Anomaly[];
}

export const AnomalyPanel: React.FC<AnomalyPanelProps> = ({ anomalies }) => {
  if (anomalies.length === 0) {
    return <div className="p-4 text-muted-foreground text-center border border-border rounded-lg bg-card">No anomalies detected.</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" aria-live="polite" role="status" aria-atomic="true">
      {anomalies.map(anomaly => (
        <AINativeCard
          key={anomaly.id}
          title={`Anomaly: ${anomaly.metric}`}
          confidenceScore={Math.min(Math.round(anomaly.deviationScore * 20), 99)}
          type="Anomaly"
          description={anomaly.description}
        >
          <div className="mt-4 pt-4 border-t border-border flex justify-between items-center text-caption text-muted-foreground">
            <span>Severity: <span className="font-medium text-foreground uppercase">{anomaly.severity}</span></span>
            <span>{new Date(anomaly.detectedAt).toLocaleTimeString()}</span>
          </div>
        </AINativeCard>
      ))}
    </div>
  );
};
