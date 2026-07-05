import { ExecutiveTable } from '@/components/tables/ExecutiveTable';
import type { SimulationOutcome } from '@/types/simulation';

interface Props {
  outcomes: SimulationOutcome[];
}

export const SimulationComparison = ({ outcomes }: Props) => {
  const columns = [
    { accessorKey: 'title', header: 'Outcome' },
    { accessorKey: 'description', header: 'Description' },
    { accessorKey: 'probability', header: 'Probability' },
    { accessorKey: 'impactScore', header: 'Impact' },
  ];

  const data = outcomes.map(outcome => ({
    id: outcome.id,
    title: outcome.title,
    description: outcome.description,
    probability: `${(outcome.probability * 100).toFixed(1)}%`,
    impactScore: outcome.impactScore.toFixed(2),
  }));

  if (!outcomes.length) return null;

  return (
    <div className="flex flex-col gap-4">
      <h3 className="text-lg font-semibold text-slate-800">Outcome Comparison</h3>
      <table className="w-full text-left sr-only">
        <caption>Comparison of Baseline vs Simulated Outcomes</caption>
        <thead>
          <tr>
            <th scope="col">Outcome</th>
            <th scope="col">Description</th>
            <th scope="col">Probability</th>
            <th scope="col">Impact</th>
          </tr>
        </thead>
        <tbody>
          {data.map(row => (
            <tr key={row.id}>
              <td>{row.title}</td>
              <td>{row.description}</td>
              <td>{row.probability}</td>
              <td>{row.impactScore}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div aria-hidden="true">
        <ExecutiveTable data={data} columns={columns as any} />
      </div>
    </div>
  );
};
