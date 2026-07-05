import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { authClient } from '@/services/authClient';
import type { ApiErrorResponse } from '@/types/api';
import { AuthShell } from './authTheme';

// Route: /reset-password?token=... — reads the token from the reset link, takes a
// new password, calls POST /api/v1/auth/reset-password, then redirects to login.
export const ResetPasswordPage: React.FC = () => {
  const [params] = useSearchParams();
  const token = params.get('token');
  const navigate = useNavigate();

  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!token) {
      setError('This reset link is invalid. Please request a new one.');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    setSubmitting(true);
    try {
      await authClient.resetPassword(token, password);
      navigate('/login', { replace: true });
    } catch (err) {
      const apiError = err as ApiErrorResponse;
      setError(apiError?.message || 'Could not reset your password. The link may have expired.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthShell>
      <form onSubmit={handleSubmit} className="auth-card">
        <div className="auth-head">
          <h1 className="auth-title">Set a new password</h1>
          <p className="auth-sub">Choose a new password for your account.</p>
        </div>

        {!token && (
          <p role="alert" className="auth-error">
            This reset link is missing its token. Please use the link from your email.
          </p>
        )}

        <label className="auth-field">
          <span>New password</span>
          <input
            type="password"
            required
            autoComplete="new-password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="auth-input"
          />
        </label>

        <label className="auth-field">
          <span>Confirm new password</span>
          <input
            type="password"
            required
            autoComplete="new-password"
            value={confirm}
            onChange={e => setConfirm(e.target.value)}
            className="auth-input"
          />
        </label>

        {error && <p role="alert" className="auth-error">{error}</p>}

        <button type="submit" disabled={submitting || !token} className="auth-submit">
          {submitting ? 'Updating…' : 'Update password'}
        </button>

        <Link to="/login" className="auth-toggle" style={{ textAlign: 'center' }}>
          Back to login
        </Link>
      </form>
    </AuthShell>
  );
};
