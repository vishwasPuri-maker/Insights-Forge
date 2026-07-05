import { OSSection } from '@/components/layout/OSSection';
import { OSGrid } from '@/components/layout/OSGrid';
import { AINativeCard } from '@/components/ai/AINativeCard';

export const SimulationEmptyState = () => {
  return (
    <div role="status" aria-live="polite">
      <OSGrid>
        <OSSection title="No Simulation Data" description="Simulation data is unavailable for this context.">
          <AINativeCard
            title="No Results"
            description="System"
            confidenceScore={0}
            type="Prediction"
          >
            <div>Please ensure the sector is fully configured to run scenarios.</div>
          </AINativeCard>
        </OSSection>
      </OSGrid>
    </div>
  );
};
