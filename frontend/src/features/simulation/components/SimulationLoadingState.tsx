import { OSSection } from '@/components/layout/OSSection';
import { OSGrid } from '@/components/layout/OSGrid';
import { AINativeCard } from '@/components/ai/AINativeCard';

export const SimulationLoadingState = () => {
  return (
    <div role="status" aria-live="polite" aria-busy="true">
      <OSGrid>
        <OSSection title="Scenario Simulation OS" description="Loading simulation analysis...">
          <AINativeCard
            title="Initializing"
            description="System"
            confidenceScore={0}
            type="Prediction"
          >
            <div className="animate-pulse h-32 bg-slate-200 rounded" />
          </AINativeCard>
        </OSSection>
      </OSGrid>
    </div>
  );
};
