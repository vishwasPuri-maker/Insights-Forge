import axios from 'axios';
import type { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import type { ApiErrorResponse } from '@/types/api';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = sessionStorage.getItem('insight-auth-storage') 
    ? JSON.parse(sessionStorage.getItem('insight-auth-storage') || '{}')?.state?.token 
    : null;
    
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<unknown>) => {
    // Backend standard error shape: { "error": { "code": "...", "message": "..." } }
    const data = error.response?.data as Record<string, unknown> | undefined;
    const errorEnvelope = (data?.error as Record<string, unknown> | undefined) ?? undefined;
    const apiError: ApiErrorResponse = {
      code: (errorEnvelope?.code as string) || 'UNKNOWN_ERROR',
      message:
        (errorEnvelope?.message as string) ||
        error.message ||
        'An unexpected error occurred',
      details: (errorEnvelope?.details as Record<string, unknown>) || {},
      status: error.response?.status,
      timestamp: new Date().toISOString(),
    };
    return Promise.reject(apiError);
  }
);
