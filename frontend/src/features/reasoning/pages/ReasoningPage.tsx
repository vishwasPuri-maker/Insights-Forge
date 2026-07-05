import React, { useState } from 'react';
import { OSLayout } from '@/components/layout/OSLayout';
import { OSSection } from '@/components/layout/OSSection';
import { useReasoning } from '../hooks/useReasoning';
import { useTenantStore } from '@/store/tenantStore';
import { ReasoningLoadingState } from '../components/ReasoningLoadingState';
import { ReasoningErrorState } from '../components/ReasoningErrorState';
import { ReasoningEmptyState } from '../components/ReasoningEmptyState';
import { ReasoningSummary } from '../components/ReasoningSummary';
import { ReasoningInsights } from '../components/ReasoningInsights';
import { ReasoningFactors } from '../components/ReasoningFactors';
import { EvidenceGraph } from '../components/EvidenceGraph';
import { EvidenceInspector } from '../components/EvidenceInspector';
import { RecommendationPanel } from '../components/RecommendationPanel';
import type { ReasoningEvidence } from '@/types/reasoning';

export const ReasoningPage: React.FC = () => {
  const { tenantId, sectorId } = useTenantStore();
  const { data, isLoading, isError } = useReasoning(tenantId, sectorId);
  const [selectedEvidence, setSelectedEvidence] = useState<ReasoningEvidence | null>(null);

  if (!tenantId || !sectorId) {
    return <ReasoningEmptyState />;
  }

  if (isLoading) {
    return <ReasoningLoadingState />;
  }

  if (isError || !data) {
    return <ReasoningErrorState />;
  }

  return (
    <>
      <OSLayout title="AI Reasoning OS" description={`Causal intelligence for ${sectorId}`}>
        
        {/* SUMMARY SECTION */}
        <OSSection title="Executive Overview" description="High-level reasoning summary">
          <ReasoningSummary summary={data.summary} confidenceScore={data.confidence.overallScore} />
        </OSSection>

        {/* ROOT CAUSE ANALYSIS */}
        <OSSection title="Root Cause Analysis" description="Factors and insights driving current anomalies">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ReasoningInsights insights={data.insights} />
            <ReasoningFactors factors={data.factors} />
          </div>
        </OSSection>

        {/* EVIDENCE GRAPH */}
        <OSSection title="Evidence Knowledge Graph" description="Causal network of reliable nodes">
          <EvidenceGraph 
            nodes={data.evidenceNodes} 
            edges={data.evidenceEdges} 
            onNodeClick={setSelectedEvidence} 
          />
        </OSSection>

        {/* RECOMMENDATION SECTION */}
        <OSSection title="Suggested Actions" description="Bridge to simulation and mitigation">
          <RecommendationPanel recommendations={data.recommendations} />
        </OSSection>

      </OSLayout>

      {/* INSPECTOR PANEL */}
      <EvidenceInspector 
        evidence={selectedEvidence} 
        onClose={() => setSelectedEvidence(null)} 
      />
    </>
  );
};
