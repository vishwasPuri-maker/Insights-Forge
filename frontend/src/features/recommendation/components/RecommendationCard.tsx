import React, { useMemo } from 'react';
import { AINativeCard } from '@/components/ai/AINativeCard';
import { KPIWidget } from '@/components/dashboard/KPIWidget';
import { ExecutiveTable } from '@/components/tables/ExecutiveTable';
import { ApprovalWorkflowComponent } from './ApprovalWorkflow';
import type { ExecutiveRecommendation, ActionPlanStep } from '@/types/recommendation';
import { Badge } from '@/components/ui/badge';
import type { ColumnDef } from '@tanstack/react-table';

interface RecommendationCardProps {
  recommendation: ExecutiveRecommendation;
}

export const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation }) => {
  const columns = useMemo<ColumnDef<ActionPlanStep, any>[]>(() => [
    {
      accessorKey: 'description',
      header: 'Step Description',
    },
    {
      accessorKey: 'owner',
      header: 'Owner',
    },
    {
      accessorKey: 'estimatedDays',
      header: 'Est. Days',
      cell: (info) => `${info.getValue()} days`
    }
  ], []);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-brand-error/10 text-brand-error border-brand-error/20';
      case 'high': return 'bg-brand-warning/10 text-brand-warning border-brand-warning/20';
      case 'medium': return 'bg-brand-info/10 text-brand-info border-brand-info/20';
      default: return 'bg-muted text-muted-foreground border-border';
    }
  };

  return (
    <AINativeCard 
      title={recommendation.title}
      description={recommendation.description}
      type="Recommendation"
      confidenceScore={Math.round(recommendation.impactScore * 100)}
      className="w-full flex flex-col space-y-6"
    >
      <div className="flex justify-between items-center mb-4">
        <Badge variant="outline" className={`capitalize ${getPriorityColor(recommendation.priority)}`}>{recommendation.priority} Priority</Badge>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <KPIWidget
          title="Projected ROI"
          value={`$${recommendation.roi.projectedValue.toLocaleString()}`}
          trend={{ value: recommendation.roi.paybackPeriodDays, direction: 'neutral', label: 'days payback' }}
        />
        <KPIWidget
          title="Impact Score"
          value={`${(recommendation.impactScore * 100).toFixed(1)}%`}
        />
        <KPIWidget
          title="Risk Score"
          value={`${(recommendation.riskScore * 100).toFixed(1)}%`}
          trend={recommendation.riskScore > 0.5 ? { value: 0, direction: 'down', label: 'High Risk' } : { value: 0, direction: 'up', label: 'Low Risk' }}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-2">
          <div className="text-h4 font-medium text-foreground">Action Plan: {recommendation.actionPlan.title}</div>
          <ExecutiveTable 
            data={recommendation.actionPlan.steps} 
            columns={columns} 
          />
        </div>
        <div className="lg:col-span-1 space-y-2">
          <div className="text-h4 font-medium text-foreground">Authorization</div>
          <ApprovalWorkflowComponent workflow={recommendation.approval} />
        </div>
      </div>
    </AINativeCard>
  );
};
