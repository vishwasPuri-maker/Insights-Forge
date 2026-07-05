import ReactECharts from 'echarts-for-react';

export const ChatVisualization = () => {
  // A simple ECharts visualization that could be rendered inline inside the chat
  const options = {
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['Q1', 'Q2', 'Q3', 'Q4'] },
    yAxis: { type: 'value' },
    series: [
      {
        data: [120, 200, 150, 80],
        type: 'bar',
        itemStyle: { color: '#6366f1' }
      }
    ]
  };

  return (
    <div className="w-full mt-3 bg-white p-2 rounded border border-gray-200">
      <h5 className="text-xs font-semibold text-gray-500 mb-2">Quarterly Revenue Context</h5>
      <ReactECharts option={options} style={{ height: '200px', width: '100%' }} />
    </div>
  );
}
