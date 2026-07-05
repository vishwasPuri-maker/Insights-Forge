import { apiClient } from '@/services/apiClient';
import type { ReportCompileRequest, ReportOut } from '@/types/report';

export const reportsClient = {
  // POST /api/v1/reports/compile
  compile: async (body: ReportCompileRequest): Promise<ReportOut> => {
    const { data } = await apiClient.post<ReportOut>('/reports/compile', body);
    return data;
  },

  // GET /api/v1/reports/{report_id}
  get: async (reportId: string): Promise<ReportOut> => {
    const { data } = await apiClient.get<ReportOut>(`/reports/${reportId}`);
    return data;
  },
};
