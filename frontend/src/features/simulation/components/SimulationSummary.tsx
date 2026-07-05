import { AINativeCard } from '@/components/ai/AINativeCard';
import { KPIWidget } from '@/components/dashboard/KPIWidget';
import type { SimulationSummary as SummaryType, SimulationConfidence } from '@/types/simulation';

interface Props {
  summary: SummaryType;
  confidence: SimulationConfidence;
  scenarioName: string;
}

export const SimulationSummary = ({ summary, confidence, scenarioName }: Props) => {
  return (
    <div role="status" aria-live="polite" aria-atomic="true" className="flex flex-col gap-4">
      <AINativeCard
        title={summary.topic}
        description="Simulation Engine"
        confidenceScore={confidence.overallScore * 100}
        type="Prediction"
      >
        <div className="flex flex-col gap-2">
          <h4 className="font-semibold text-slate-800">Scenario: {scenarioName}</h4>
          <p className="text-slate-600">{summary.executiveSummary}</p>
          <p className="text-slate-700 font-medium">{summary.primaryConclusion}</p>
        </div>
      </AINativeCard>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <KPIWidget
          title="Data Quality"
          value={confidence.dataQualityScore * 100}
          trend={{ direction: 'neutral', value: 0, label: 'Model Certainty: ' + (confidence.modelCertainty * 100).toFixed(1) + '%' }}
        />
      </div>
    </div>
  );
};
