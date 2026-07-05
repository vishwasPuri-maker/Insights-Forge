import { describe, it, expect } from 'vitest';
import { apiClient } from '../apiClient';
import { http, HttpResponse } from 'msw';
import { server } from '../../mocks/server';

describe('apiClient', () => {
  it('handles global 500 error mapping correctly', async () => {
    server.use(
      http.get('/api/v1/test-500', () => HttpResponse.json({ code: 'SERVER_ERROR', message: 'Internal server error' }, { status: 500 }))
    );
    await expect(apiClient.get('/test-500')).rejects.toMatchObject({ code: 'SERVER_ERROR', message: 'Internal server error' });
  });

  it('handles 401 correctly by propagating canonical format', async () => {
    server.use(
      http.get('/api/v1/test-401', () => HttpResponse.json({ code: 'UNAUTHORIZED', message: 'Token expired' }, { status: 401 }))
    );
    await expect(apiClient.get('/test-401')).rejects.toMatchObject({ code: 'UNAUTHORIZED', message: 'Token expired' });
  });

  it('handles 403 RBAC failure', async () => {
    server.use(
      http.get('/api/v1/test-403', () => HttpResponse.json({ code: 'FORBIDDEN', message: 'Insufficient privileges' }, { status: 403 }))
    );
    await expect(apiClient.get('/test-403')).rejects.toMatchObject({ code: 'FORBIDDEN' });
  });

  it('handles network timeouts', async () => {
    await expect(apiClient.get('http://non-existent-url.local/timeout', { timeout: 1 })).rejects.toMatchObject({ code: 'UNKNOWN_ERROR' });
  });
  
  it('injects bearer token into headers if available', async () => {
    sessionStorage.setItem('insight-auth-storage', JSON.stringify({ state: { token: 'my-token' } }));
    server.use(
      http.get('/api/v1/test-auth', ({ request }) => {
        expect(request.headers.get('Authorization')).toBe('Bearer my-token');
        return HttpResponse.json({ success: true });
      })
    );
    await apiClient.get('/test-auth');
    sessionStorage.clear();
  });
});
