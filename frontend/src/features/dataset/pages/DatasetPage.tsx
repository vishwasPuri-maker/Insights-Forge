import React, { useRef } from 'react';
import { OSLayout } from '@/components/layout/OSLayout';
import { OSSection } from '@/components/layout/OSSection';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useDatasets, useRecords, useIngestion } from '../hooks/useDatasets';

export const DatasetPage: React.FC = () => {
  const { data: datasets, isLoading, isError } = useDatasets();
  const { data: records } = useRecords();
  const ingestion = useIngestion();
  const fileInput = useRef<HTMLInputElement>(null);

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) ingestion.mutate(file);
    e.target.value = '';
  };

  return (
    <OSLayout title="Dataset Management OS" description="Upload, track and inspect cleaned data">
      <OSSection title="Ingest data" description="Streams to the landing bucket via POST /ingestion/stream">
        <Card>
          <CardContent className="pt-6 flex items-center gap-3">
            <input ref={fileInput} type="file" className="hidden" onChange={handleFile} />
            <Button onClick={() => fileInput.current?.click()} disabled={ingestion.isPending}>
              {ingestion.isPending ? 'Uploading…' : 'Upload file'}
            </Button>
            {ingestion.data && (
              <span className="text-sm text-muted-foreground">
                Created dataset {ingestion.data.dataset_id} ({ingestion.data.status})
              </span>
            )}
            {ingestion.isError && (
              <span className="text-sm text-brand-error">
                {(ingestion.error as { message?: string })?.message || 'Upload failed.'}
              </span>
            )}
          </CardContent>
        </Card>
      </OSSection>

      <OSSection title="Datasets" description="GET /datasets — status + health score">
        <Card>
          <CardContent className="pt-6">
            {isLoading && <p className="text-muted-foreground">Loading datasets…</p>}
            {isError && <p className="text-brand-error">Failed to load datasets.</p>}
            {datasets && datasets.length === 0 && (
              <p className="text-muted-foreground">No datasets yet.</p>
            )}
            {datasets && datasets.length > 0 && (
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-muted-foreground border-b border-border">
                    <th className="py-2">Filename</th>
                    <th className="py-2">Sector</th>
                    <th className="py-2">Status</th>
                    <th className="py-2 text-right">Health</th>
                  </tr>
                </thead>
                <tbody>
                  {datasets.map((d) => (
                    <tr key={d.id} className="border-b border-border/50">
                      <td className="py-2 font-medium">{d.original_filename}</td>
                      <td className="py-2">{d.sector}</td>
                      <td className="py-2">
                        <Badge variant="secondary">{d.status}</Badge>
                      </td>
                      <td className="py-2 text-right">
                        {d.health_score != null ? `${d.health_score}` : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </CardContent>
        </Card>
      </OSSection>

      <OSSection title="Cleaned records" description="GET /sectors/{sector}/records">
        <Card>
          <CardContent className="pt-6">
            {!records && <p className="text-muted-foreground">Loading records…</p>}
            {records && (
              <>
                <p className="text-sm text-muted-foreground mb-2">
                  {records.total} record(s) in {records.sector}
                </p>
                <ul className="text-sm space-y-1">
                  {records.items.slice(0, 10).map((r) => (
                    <li key={r.id} className="border-b border-border/50 py-1 font-mono truncate">
                      {JSON.stringify(r.data)}
                    </li>
                  ))}
                </ul>
              </>
            )}
          </CardContent>
        </Card>
      </OSSection>
    </OSLayout>
  );
};
