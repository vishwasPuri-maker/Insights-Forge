// Matches ReportOut / ReportCompileRequest in openapi.json.

export interface ReportCompileRequest {
  report_type: string;
  params?: Record<string, unknown> | null;
}

export interface ReportOut {
  id: string;
  sector: string;
  report_type: string;
  status: string;
  download_url?: string | null;
  created_at: string;
}
