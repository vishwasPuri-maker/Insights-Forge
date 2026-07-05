import { useState } from 'react';
import { OSLayout } from '@/components/layout/OSLayout';
import { OSSection } from '@/components/layout/OSSection';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useSimulate } from '../hooks/useSimulate';
import type { SimulateMetric } from '@/types/simulate';

interface MetricRow {
  key: string;
  current: string;
  change_pct: string;
}

const DEFAULT_ROWS: MetricRow[] = [
  { key: 'revenue', current: '10000', change_pct: '5' },
  { key: 'units', current: '500', change_pct: '-2' },
];

export const SimulationPage = () => {
  const [rows, setRows] = useState<MetricRow[]>(DEFAULT_ROWS);
  const simulate = useSimulate();

  const updateRow = (i: number, field: keyof MetricRow, value: string) => {
    setRows((prev) => prev.map((r, idx) => (idx === i ? { ...r, [field]: value } : r)));
  };

  const addRow = () => setRows((prev) => [...prev, { key: '', current: '0', change_pct: '0' }]);
  const removeRow = (i: number) => setRows((prev) => prev.filter((_, idx) => idx !== i));

  const handleRun = () => {
    const metrics: SimulateMetric[] = rows
      .filter((r) => r.key.trim().length > 0)
      .map((r) => ({
        key: r.key.trim(),
        current: Number(r.current) || 0,
        change_pct: Number(r.change_pct) || 0,
      }));
    if (metrics.length === 0) return;
    simulate.mutate({ metrics });
  };

  const result = simulate.data;

  return (
    <OSLayout title="Scenario Simulation OS" description="What-if projection via POST /simulate">
      <OSSection title="Metrics" description="Adjust current values and % change, then run the simulation">
        <Card>
          <CardContent className="pt-6 flex flex-col gap-3">
            <div className="grid grid-cols-[1fr_1fr_1fr_auto] gap-3 text-sm text-muted-foreground font-medium">
              <span>Metric key</span>
              <span>Current</span>
              <span>Change %</span>
              <span />
            </div>
            {rows.map((row, i) => (
              <div key={i} className="grid grid-cols-[1fr_1fr_1fr_auto] gap-3 items-center">
                <Input
                  value={row.key}
                  placeholder="metric_key"
                  onChange={(e) => updateRow(i, 'key', e.target.value)}
                />
                <Input
                  type="number"
                  value={row.current}
                  onChange={(e) => updateRow(i, 'current', e.target.value)}
                />
                <Input
                  type="number"
                  value={row.change_pct}
                  onChange={(e) => updateRow(i, 'change_pct', e.target.value)}
                />
                <Button variant="ghost" size="sm" onClick={() => removeRow(i)}>
                  Remove
                </Button>
              </div>
            ))}
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={addRow}>
                Add metric
              </Button>
              <Button size="sm" onClick={handleRun} disabled={simulate.isPending}>
                {simulate.isPending ? 'Running…' : 'Run simulation'}
              </Button>
            </div>
          </CardContent>
        </Card>
      </OSSection>

      {simulate.isError && (
        <div className="p-4 text-brand-error bg-brand-error/5 border border-brand-error/20 rounded-lg">
          {(simulate.error as { message?: string })?.message || 'Simulation failed.'}
        </div>
      )}

      {result && (
        <OSSection
          title="Projections"
          description={`Sector: ${result.sector} · Total ${result.total_current.toLocaleString()} → ${result.total_projected.toLocaleString()}`}
        >
          <Card>
            <CardContent className="pt-6">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b border-border">
                    <th className="py-2">Metric</th>
                    <th className="py-2 text-right">Current</th>
                    <th className="py-2 text-right">Projected</th>
                    <th className="py-2 text-right">Change %</th>
                  </tr>
                </thead>
                <tbody>
                  {result.projections.map((p) => (
                    <tr key={p.key} className="border-b border-border/50">
                      <td className="py-2 font-medium">{p.key}</td>
                      <td className="py-2 text-right">{p.current.toLocaleString()}</td>
                      <td className="py-2 text-right">{p.projected.toLocaleString()}</td>
                      <td
                        className={`py-2 text-right ${p.change_pct >= 0 ? 'text-brand-success' : 'text-brand-error'}`}
                      >
                        {p.change_pct >= 0 ? '+' : ''}
                        {p.change_pct}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </OSSection>
      )}
    </OSLayout>
  );
};
