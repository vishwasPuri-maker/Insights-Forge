import React from 'react';
import ReactECharts from 'echarts-for-react';

const ChartRenderer = ({ chartConfig }) => {
  if (!chartConfig) return null;

  // Set default modern dark theme styling for ECharts
  const modernOptions = {
    ...chartConfig,
    backgroundColor: 'transparent',
    textStyle: {
      fontFamily: 'Inter, "Roboto Mono", monospace',
      color: 'var(--text-secondary)'
    },
    tooltip: {
      ...chartConfig.tooltip,
      backgroundColor: 'rgba(13, 17, 23, 0.9)',
      borderColor: 'var(--border-color)',
      textStyle: { color: 'var(--text-primary)' }
    },
  };

  return (
    <div className="chart-container" style={{ width: '100%', height: '300px', marginTop: '1rem' }}>
      <ReactECharts
        option={modernOptions}
        style={{ height: '100%', width: '100%' }}
        theme="dark"
      />
    </div>
  );
};

export default ChartRenderer;
