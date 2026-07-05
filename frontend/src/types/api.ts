export interface ApiErrorResponse {
  code: string;
  message: string;
  // HTTP status of the failed response (used e.g. to detect a 403 "email not
  // verified" on login). Undefined for network/timeout errors with no response.
  status?: number;
  details?: Record<string, unknown>;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  size: number;
  has_more: boolean;
}

export type ApiVersion = 'v1' | 'v2';
