import { describe, it, expect } from 'vitest';
import { mapReasoningAnalysis } from '../api/reasoningMapper';
import type { ReasoningAnalysisDTO } from '@/types/reasoning';

describe('reasoningMapper', () => {
  it('maps ReasoningAnalysisDTO to ReasoningAnalysis deterministically', () => {
    const mockDTO: ReasoningAnalysisDTO = {
      id: 'test-id',
      tenant_id: 'tenant-1',
      sector_id: 'sector-1',
      summary: {
        topic: 'Test Topic',
        executive_summary: 'Test summary.',
        primary_conclusion: 'Test conclusion.'
      },
      insights: [
        {
          id: 'i1',
          title: 'Insight 1',
          description: 'Desc 1',
          severity: 'high',
          category: 'anomaly'
        }
      ],
      factors: [
        {
          id: 'f1',
          name: 'Factor 1',
          contribution_weight: 0.8,
          trend: 'increasing'
        }
      ],
      evidence_nodes: [
        {
          id: 'e1',
          source: 'System',
          description: 'Log 1',
          reliability: 0.9
        }
      ],
      evidence_edges: [
        {
          id: 'edge1',
          source_id: 'e1',
          target_id: 'e2',
          relationship: 'causes',
          strength: 0.75
        }
      ],
      recommendations: [
        {
          id: 'r1',
          title: 'Fix issue',
          description: 'Fix it now.',
          impact_score: 0.99,
          effort_level: 'low',
          action_type: 'mitigate'
        }
      ],
      confidence: {
        overall_score: 0.85,
        data_quality_score: 0.90,
        model_certainty: 0.80
      },
      metadata: {
        generated_at: '2026-07-01T00:00:00Z',
        model_id: 'model-a',
        processing_time_ms: 500
      }
    };

    const domain = mapReasoningAnalysis(mockDTO);

    expect(domain.id).toBe(mockDTO.id);
    expect(domain.tenantId).toBe(mockDTO.tenant_id);
    expect(domain.sectorId).toBe(mockDTO.sector_id);
    
    expect(domain.summary.topic).toBe(mockDTO.summary.topic);
    expect(domain.summary.executiveSummary).toBe(mockDTO.summary.executive_summary);
    expect(domain.summary.primaryConclusion).toBe(mockDTO.summary.primary_conclusion);

    expect(domain.insights[0].id).toBe(mockDTO.insights[0].id);
    expect(domain.insights[0].severity).toBe(mockDTO.insights[0].severity);
    expect(domain.insights[0].category).toBe(mockDTO.insights[0].category);

    expect(domain.factors[0].contributionWeight).toBe(mockDTO.factors[0].contribution_weight);

    expect(domain.evidenceNodes[0].source).toBe(mockDTO.evidence_nodes[0].source);

    expect(domain.evidenceEdges[0].sourceId).toBe(mockDTO.evidence_edges[0].source_id);
    expect(domain.evidenceEdges[0].targetId).toBe(mockDTO.evidence_edges[0].target_id);

    expect(domain.recommendations[0].impactScore).toBe(mockDTO.recommendations[0].impact_score);
    expect(domain.recommendations[0].effortLevel).toBe(mockDTO.recommendations[0].effort_level);
    expect(domain.recommendations[0].actionType).toBe(mockDTO.recommendations[0].action_type);

    expect(domain.confidence.overallScore).toBe(mockDTO.confidence.overall_score);
    expect(domain.confidence.dataQualityScore).toBe(mockDTO.confidence.data_quality_score);
    expect(domain.confidence.modelCertainty).toBe(mockDTO.confidence.model_certainty);

    expect(domain.metadata.generatedAt).toBe(mockDTO.metadata.generated_at);
    expect(domain.metadata.modelId).toBe(mockDTO.metadata.model_id);
    expect(domain.metadata.processingTimeMs).toBe(mockDTO.metadata.processing_time_ms);
  });
});
