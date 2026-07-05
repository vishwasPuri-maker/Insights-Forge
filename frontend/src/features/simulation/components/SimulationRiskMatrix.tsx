import { ExecutiveTable } from '@/components/tables/ExecutiveTable';
import type { SimulationRisk } from '@/types/simulation';

interface Props {
  risks: SimulationRisk[];
}

export const SimulationRiskMatrix = ({ risks }: Props) => {
  const columns = [
    { accessorKey: 'description', header: 'Risk Description' },
    { accessorKey: 'severity', header: 'Severity' },
    { accessorKey: 'mitigationStrategy', header: 'Mitigation' }
  ];

  if (!risks.length) return null;

  return (
    <div className="flex flex-col gap-4">
      <h3 className="text-lg font-semibold text-slate-800">Risk Matrix</h3>
      <table className="w-full text-left sr-only">
        <caption>Identified Risks and Mitigation Strategies</caption>
        <thead>
          <tr>
            <th scope="col">Description</th>
            <th scope="col">Severity</th>
            <th scope="col">Mitigation</th>
          </tr>
        </thead>
        <tbody>
          {risks.map(risk => (
            <tr key={risk.id}>
              <td>{risk.description}</td>
              <td>{risk.severity}</td>
              <td>{risk.mitigationStrategy}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div aria-hidden="true">
        <ExecutiveTable data={risks as any} columns={columns as any} />
      </div>
    </div>
  );
};
