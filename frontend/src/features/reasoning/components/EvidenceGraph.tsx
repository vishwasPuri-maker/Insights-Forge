import React, { useMemo } from 'react';
import { BaseChart } from '@/components/charts/BaseChart';
import { ExecutiveTable } from '@/components/tables/ExecutiveTable';
import type { ReasoningEvidence, ReasoningEdge } from '@/types/reasoning';

interface EvidenceGraphProps {
  nodes: ReasoningEvidence[];
  edges: ReasoningEdge[];
  onNodeClick: (node: ReasoningEvidence) => void;
}

export const EvidenceGraph: React.FC<EvidenceGraphProps> = ({ nodes, edges, onNodeClick }) => {
  // Hard safety limit to prevent main thread blocking
  const isSimplified = nodes.length > 100;

  const chartOptions = useMemo(() => {
    if (isSimplified) return {};

    const graphNodes = nodes.map(n => ({
      id: n.id,
      name: n.source,
      value: Math.round(n.reliability * 100),
      symbolSize: Math.max(20, n.reliability * 50),
      itemStyle: {
        color: n.reliability > 0.8 ? '#10b981' : n.reliability > 0.5 ? '#f59e0b' : '#ef4444'
      }
    }));

    const graphEdges = edges.map(e => ({
      source: e.sourceId,
      target: e.targetId,
      lineStyle: { width: Math.max(1, e.strength * 5) }
    }));

    return {
      tooltip: { formatter: '{b} (Reliability: {c}%)' },
      series: [{
        type: 'graph' as const,
        layout: 'force' as const,
        data: graphNodes,
        links: graphEdges,
        roam: true,
        label: { show: true, position: 'right' as const },
        force: { repulsion: 200 }
      }]
    };
  }, [nodes, edges, isSimplified]);

  const columns = [
    { accessorKey: 'source', header: 'Source' },
    { accessorKey: 'description', header: 'Description' },
    { accessorKey: 'reliability', header: 'Reliability', cell: (info: unknown) => `${Math.round((info as { getValue: () => number }).getValue() * 100)}%` }
  ];

  if (isSimplified) {
    return (
      <div className="space-y-4">
        <div className="p-4 bg-muted text-muted-foreground text-sm rounded-md border border-border">
          Graph visualization hidden because node count exceeds 100. Displaying accessible tabular data instead.
        </div>
        <ExecutiveTable data={nodes} columns={columns} />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div aria-hidden="true" className="h-[400px] w-full border border-border rounded-md bg-card">
        <BaseChart 
          option={chartOptions} 
          height="400px"
          onEvents={{
            click: (params: unknown) => {
              const p = params as { dataType: string; data: { id: string } };
              if (p.dataType === 'node') {
                const node = nodes.find(n => n.id === p.data.id);
                if (node) onNodeClick(node);
              }
            }
          }} 
        />
      </div>
      <div className="sr-only">
        {/* Screen reader only parallel representation */}
        <ExecutiveTable data={nodes} columns={columns} />
      </div>
    </div>
  );
};
