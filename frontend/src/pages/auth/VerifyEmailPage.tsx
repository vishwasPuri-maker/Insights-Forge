import React, { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { authClient } from '@/services/authClient';
import type { ApiErrorResponse } from '@/types/api';
import { AuthShell } from './authTheme';

type Status = 'verifying' | 'success' | 'error' | 'missing';

// Route: /verify-email?token=...  — reads the token from the verification link,
// calls POST /api/v1/auth/verify-email, and reports the outcome.
export const VerifyEmailPage: React.FC = () => {
  const [params] = useSearchParams();
  const token = params.get('token');
  const [status, setStatus] = useState<Status>(token ? 'verifying' : 'missing');
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    let active = true;
    authClient
      .verifyEmail(token)
      .then(() => active && setStatus('success'))
      .catch((err: ApiErrorResponse) => {
        if (!active) return;
        setMessage(err?.message || 'This verification link is invalid or has expired.');
        setStatus('error');
      });
    return () => {
      active = false;
    };
  }, [token]);

  return (
    <AuthShell>
      <div className="auth-card">
        <div className="auth-head">
          <h1 className="auth-title">
            {status === 'success' ? 'Email verified' : 'Verify your email'}
          </h1>
          <p className="auth-sub">
            {status === 'verifying' && 'Confirming your email address…'}
            {status === 'success' && 'Email verified — you can now log in.'}
            {status === 'missing' &&
              'This page needs a verification link. Please open the link from your email.'}
            {status === 'error' && (message ?? 'Verification failed.')}
          </p>
        </div>

        {status === 'error' && message && (
          <p role="alert" className="auth-error">{message}</p>
        )}

        {(status === 'success' || status === 'error' || status === 'missing') && (
          <Link to="/login" className="auth-submit" style={{ textAlign: 'center' }}>
            Go to login
          </Link>
        )}
      </div>
    </AuthShell>
  );
};
