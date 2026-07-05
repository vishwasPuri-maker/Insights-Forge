import { Badge } from '@/components/ui/badge';
import type { SimulationRecommendation } from '@/types/simulation';

interface Props {
  recommendations: SimulationRecommendation[];
}

export const SimulationRecommendationBridge = ({ recommendations }: Props) => {
  if (!recommendations.length) return null;

  return (
    <div className="flex flex-col gap-4">
      {recommendations.map(rec => (
        <div key={rec.id} className="flex flex-col sm:flex-row gap-4 p-4 rounded-lg border bg-card">
          <div className="flex-1">
            <h4 className="font-semibold text-slate-800">{rec.title}</h4>
            <p className="text-sm text-slate-600 mt-1">{rec.description}</p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <Badge variant="outline">{rec.actionType}</Badge>
            <div className="text-sm text-slate-500">Impact: {(rec.impactScore * 100).toFixed(0)}%</div>
            <div className="text-sm text-slate-500">Effort: {rec.effortLevel}</div>
          </div>
        </div>
      ))}
    </div>
  );
};
