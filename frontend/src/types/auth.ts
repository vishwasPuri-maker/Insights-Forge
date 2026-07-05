// Backend RBAC roles (see UserCreate.role in openapi.json)
export type UserRole = 'admin' | 'manager' | 'user';

// POST /api/v1/auth/login request body (LoginRequest)
export interface LoginRequest {
  email: string;
  password: string;
}

// POST /api/v1/auth/signup request body (SignupRequest)
export interface SignupRequest {
  organization_name: string;
  email: string;
  password: string;
  sector: 'retail' | 'service' | 'education' | 'agriculture';
}

// POST /api/v1/auth/refresh and /auth/logout request body (RefreshRequest)
export interface RefreshRequest {
  refresh_token: string;
}

// POST /api/v1/auth/verify-email request body (VerifyEmailRequest) -> 204
export interface VerifyEmailRequest {
  token: string;
}

// POST /api/v1/auth/forgot-password request body (ForgotPasswordRequest) -> 202
export interface ForgotPasswordRequest {
  email: string;
}

// POST /api/v1/auth/reset-password request body (ResetPasswordRequest) -> 204
export interface ResetPasswordRequest {
  token: string;
  new_password: string;
}

// TokenResponse — returned by /auth/login and /auth/refresh
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type?: string;
}

// UserOut (GET /api/v1/users). Note: backend keys the tenant as organization_id.
export interface User {
  id: string;
  organization_id: string;
  email: string;
  role: string;
  sector: string;
  created_at: string;
}
