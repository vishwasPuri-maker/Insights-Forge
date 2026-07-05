import React, { useMemo } from 'react';
import type { GovernanceHealthMetric } from '@/types/governance';
import { BaseChart } from '@/components/charts/BaseChart';
import { ExecutiveTable } from '@/components/tables/ExecutiveTable';
import { createColumnHelper } from '@tanstack/react-table';
import type { EChartsOption } from 'echarts';

interface SystemHealthProps {
  metrics: GovernanceHealthMetric[];
}

interface MetricRow {
  id: string;
  metricName: string;
  value: string;
  timestamp: string;
}

const columnHelper = createColumnHelper<MetricRow>();

export const SystemHealth: React.FC<SystemHealthProps> = ({ metrics }) => {
  const chartOption = useMemo<EChartsOption>(() => {
    return {
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: metrics.map(m => new Date(m.timestamp).toLocaleTimeString()),
        show: false
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: 'System Health',
          type: 'line',
          smooth: true,
          data: metrics.map(m => m.value),
          areaStyle: { color: 'rgba(59, 130, 246, 0.2)' },
          lineStyle: { color: 'rgb(59, 130, 246)' }
        }
      ]
    };
  }, [metrics]);

  const columns = [
    columnHelper.accessor('metricName', { header: 'Metric' }),
    columnHelper.accessor('value', { header: 'Value' }),
    columnHelper.accessor('timestamp', { header: 'Timestamp' }),
  ];

  const rowData: MetricRow[] = metrics.map(m => ({
    id: m.id,
    metricName: m.metricName,
    value: `${m.value} ${m.unit}`,
    timestamp: new Date(m.timestamp).toLocaleTimeString(),
  }));

  return (
    <div className="flex flex-col gap-4 w-full h-[400px]">
      <div className="h-48 w-full border rounded-md border-border bg-card p-4 overflow-hidden" aria-hidden="true">
        {metrics.length > 0 ? (
          <BaseChart option={chartOption} />
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">No telemetry data.</div>
        )}
      </div>
      <div className="flex-1 overflow-auto">
        <ExecutiveTable 
          columns={columns}
          data={rowData}
        />
      </div>
    </div>
  );
};
