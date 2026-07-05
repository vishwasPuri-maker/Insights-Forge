import ReactECharts from 'echarts-for-react';

export const TimeSeriesChart = () => {
  const options = {
    title: { text: 'Predictive Demand Matrix' },
    tooltip: { trigger: 'axis' },
    legend: { data: ['Historical Demand', 'Projected Shortage'] },
    xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
    yAxis: { type: 'value' },
    series: [
      {
        name: 'Historical Demand',
        type: 'line',
        data: [120, 132, 101, 134, 90, 230, 210],
        smooth: true,
        itemStyle: { color: '#3b82f6' }
      },
      {
        name: 'Projected Shortage',
        type: 'line',
        data: [220, 182, 191, 234, 290, 330, 310],
        smooth: true,
        itemStyle: { color: '#ef4444' }
      }
    ]
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mt-6">
      <ReactECharts option={options} style={{ height: '400px', width: '100%' }} />
    </div>
  );
}
