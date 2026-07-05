// Matches IngestionResponse in openapi.json.
export interface IngestionResponse {
  dataset_id: string;
  sector: string;
  status: string;
  size_bytes?: number | null;
}
