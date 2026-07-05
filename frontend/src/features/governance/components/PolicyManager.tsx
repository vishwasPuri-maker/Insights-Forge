import React from 'react';
import type { GovernancePolicy, GovernanceAlert } from '@/types/governance';
import { AINativeCard } from '@/components/ai/AINativeCard';

interface PolicyManagerProps {
  policies: GovernancePolicy[];
  criticalAlerts: GovernanceAlert[];
}

export const PolicyManager: React.FC<PolicyManagerProps> = ({ policies, criticalAlerts }) => {
  return (
    <div className="flex flex-col gap-4">
      {criticalAlerts.length > 0 && (
        <div role="status" aria-live="polite" className="p-4 border border-destructive bg-destructive/10 text-destructive rounded-md">
          <h4 className="font-bold mb-2">Critical Violations Detected</h4>
          <ul className="list-disc pl-4 space-y-1">
            {criticalAlerts.map(alert => (
              <li key={alert.id} className="text-sm">
                <span className="font-semibold">{alert.type}:</span> {alert.message}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {policies.map(policy => (
          <AINativeCard key={policy.id} title={policy.name} description={policy.description} type="Anomaly" confidenceScore={1} className="p-4 flex flex-col gap-2 relative">
            <div className="flex justify-between items-start">
              <span 
                className={`px-2 py-1 text-xs rounded-full border ${policy.enforced ? 'border-primary text-primary bg-primary/10' : 'border-muted text-muted-foreground bg-muted/20'}`}
              >
                {policy.enforced ? 'Enforced' : 'Monitor Only'}
              </span>
            </div>
            <div className="mt-auto pt-2 flex justify-end">
              <button className="text-xs px-3 py-1 border rounded hover:bg-muted" aria-label={`Configure ${policy.name}`}>Configure</button>
            </div>
          </AINativeCard>
        ))}
        {policies.length === 0 && (
          <div className="col-span-2 text-center text-muted-foreground p-4">No active policies.</div>
        )}
      </div>
    </div>
  );
};
