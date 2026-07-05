// Matches RecordOut / RecordsPage in openapi.json.

export interface RecordOut {
  id: string;
  dataset_id: string;
  sector: string;
  data: Record<string, unknown>;
  recorded_at?: string | null;
  created_at: string;
}

export interface RecordsPage {
  sector: string;
  total: number;
  limit: number;
  offset: number;
  items: RecordOut[];
}
