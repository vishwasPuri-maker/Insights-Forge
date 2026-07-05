import React, { useState } from 'react';
import { OSLayout } from '@/components/layout/OSLayout';
import { OSSection } from '@/components/layout/OSSection';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { useCompileReport, useReport } from '../hooks/useReports';

export const ReportingPage: React.FC = () => {
  const [reportType, setReportType] = useState('executive');
  const [reportId, setReportId] = useState<string | null>(null);

  const compile = useCompileReport();
  const { data: report } = useReport(reportId);

  const handleCompile = () => {
    if (!reportType.trim()) return;
    compile.mutate(
      { report_type: reportType.trim() },
      { onSuccess: (r) => setReportId(r.id) },
    );
  };

  // Prefer the polled detail; fall back to the compile response.
  const current = report ?? compile.data ?? null;

  return (
    <OSLayout title="Reporting OS" description="Compile and download sector reports">
      <OSSection title="Compile a report" description="Kicks off POST /reports/compile">
        <Card>
          <CardContent className="pt-6 flex items-end gap-3">
            <label className="flex flex-col gap-1 text-sm flex-1 max-w-xs">
              <span className="text-muted-foreground">Report type</span>
              <Input value={reportType} onChange={(e) => setReportType(e.target.value)} />
            </label>
            <Button onClick={handleCompile} disabled={compile.isPending}>
              {compile.isPending ? 'Compiling…' : 'Compile'}
            </Button>
          </CardContent>
        </Card>
      </OSSection>

      {compile.isError && (
        <div className="p-4 text-brand-error bg-brand-error/5 border border-brand-error/20 rounded-lg">
          {(compile.error as { message?: string })?.message || 'Failed to compile report.'}
        </div>
      )}

      {current && (
        <OSSection title="Report status" description={`Report ${current.id}`}>
          <Card>
            <CardContent className="pt-6 flex items-center justify-between gap-4">
              <div>
                <p className="font-medium">{current.report_type}</p>
                <p className="text-sm text-muted-foreground">Sector: {current.sector}</p>
              </div>
              <Badge variant="secondary">{current.status}</Badge>
              {current.download_url ? (
                <a
                  href={current.download_url}
                  className="text-brand-info underline"
                  target="_blank"
                  rel="noreferrer"
                >
                  Download
                </a>
              ) : (
                <span className="text-sm text-muted-foreground">Preparing…</span>
              )}
            </CardContent>
          </Card>
        </OSSection>
      )}
    </OSLayout>
  );
};
