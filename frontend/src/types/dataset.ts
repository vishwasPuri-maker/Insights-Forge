// DatasetOut — matches GET /api/v1/datasets in openapi.json.
export interface DatasetMetadata {
  id: string;
  sector: string;
  original_filename: string;
  status: string;
  health_score?: number | null;
  size_bytes?: number | null;
  content_type?: string | null;
  uploaded_by: string;
  created_at: string;
}
