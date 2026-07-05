import { apiClient } from './apiClient';
import type {
  LoginRequest,
  SignupRequest,
  TokenResponse,
  VerifyEmailRequest,
  ForgotPasswordRequest,
  ResetPasswordRequest,
} from '@/types/auth';

export const authClient = {
  // POST /api/v1/auth/login -> TokenResponse { access_token, refresh_token }
  login: async (credentials: LoginRequest): Promise<TokenResponse> => {
    const { data } = await apiClient.post<TokenResponse>('/auth/login', credentials);
    return data;
  },

  // POST /api/v1/auth/signup -> TokenResponse (creates the org + first user)
  signup: async (payload: SignupRequest): Promise<TokenResponse> => {
    const { data } = await apiClient.post<TokenResponse>('/auth/signup', payload);
    return data;
  },

  // POST /api/v1/auth/refresh -> TokenResponse
  refresh: async (refreshToken: string): Promise<TokenResponse> => {
    const { data } = await apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return data;
  },

  // POST /api/v1/auth/logout (requires the refresh token in the body)
  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post('/auth/logout', { refresh_token: refreshToken });
  },

  // POST /api/v1/auth/verify-email -> 204. Confirms the email via the token
  // delivered in the verification link (?token=...).
  verifyEmail: async (token: string): Promise<void> => {
    const body: VerifyEmailRequest = { token };
    await apiClient.post('/auth/verify-email', body);
  },

  // POST /api/v1/auth/forgot-password -> 202. Always succeeds (no user enumeration);
  // the backend only sends a reset link if the email exists.
  forgotPassword: async (email: string): Promise<void> => {
    const body: ForgotPasswordRequest = { email };
    await apiClient.post('/auth/forgot-password', body);
  },

  // POST /api/v1/auth/reset-password -> 204. Sets a new password using the token
  // from the reset link (?token=...).
  resetPassword: async (token: string, newPassword: string): Promise<void> => {
    const body: ResetPasswordRequest = { token, new_password: newPassword };
    await apiClient.post('/auth/reset-password', body);
  },
};
