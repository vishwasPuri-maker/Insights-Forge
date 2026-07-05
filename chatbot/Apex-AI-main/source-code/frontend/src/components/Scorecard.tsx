interface ScorecardProps {
  title: string;
  value: string;
  trend: string;
  isPositive: boolean;
}

export const Scorecard = ({ title, value, trend, isPositive }: ScorecardProps) => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col">
      <h4 className="text-sm font-medium text-gray-500 mb-2">{title}</h4>
      <div className="flex items-end justify-between">
        <span className="text-3xl font-bold text-gray-900">{value}</span>
        <span className={`text-sm font-semibold flex items-center ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
          {isPositive ? '↑' : '↓'} {trend}
        </span>
      </div>
    </div>
  )
}

export const ScorecardRow = () => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Scorecard title="GMROI" value="1.45" trend="5.2%" isPositive={true} />
      <Scorecard title="Capacity Utilization" value="82%" trend="1.1%" isPositive={true} />
      <Scorecard title="CSAT Score" value="4.8/5" trend="0.2%" isPositive={true} />
      <Scorecard title="Active Anomalies" value="12" trend="15%" isPositive={false} />
    </div>
  )
}
