import React from 'react';
import type { GovernanceSummary as GovernanceSummaryModel } from '@/types/governance';
import { AINativeCard } from '@/components/ai/AINativeCard';
import { KPIWidget } from '@/components/dashboard/KPIWidget';
import { ConfidencePanel } from '@/features/reasoning/components/ConfidencePanel';
import { OSGrid } from '@/components/layout/OSGrid';

interface GovernanceSummaryProps {
  summary: GovernanceSummaryModel;
}

export const GovernanceSummary: React.FC<GovernanceSummaryProps> = React.memo(({ summary }) => {
  return (
    <div role="status" aria-live="polite" className="w-full">
      <OSGrid>
        <KPIWidget
          title="Active Users"
          value={summary.activeUsers}
          trend={{ value: 5, direction: 'up', label: 'vs last week' }}
        />
        <KPIWidget
          title="Critical Alerts"
          value={summary.openAlerts}
          trend={summary.openAlerts > 0 ? { value: summary.openAlerts, direction: 'up', label: 'needs action' } : undefined}
        />
        <KPIWidget
          title="Pending Approvals"
          value={summary.pendingApprovals}
        />
        <AINativeCard title="Compliance Score" description="System compliance rating" type="Prediction" confidenceScore={summary.systemHealthScore / 100}>
          <ConfidencePanel score={summary.systemHealthScore / 100} label="System Health" />
        </AINativeCard>
      </OSGrid>
    </div>
  );
});

GovernanceSummary.displayName = 'GovernanceSummary';
