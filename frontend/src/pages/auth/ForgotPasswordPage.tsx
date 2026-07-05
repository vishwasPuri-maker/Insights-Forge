import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authClient } from '@/services/authClient';
import type { ApiErrorResponse } from '@/types/api';
import { AuthShell } from './authTheme';

// Route: /forgot-password — collects an email and calls
// POST /api/v1/auth/forgot-password. The backend never reveals whether the
// email exists, so we always show the same neutral confirmation on success.
export const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await authClient.forgotPassword(email);
      setSent(true);
    } catch (err) {
      const apiError = err as ApiErrorResponse;
      setError(apiError?.message || 'Could not send the reset link. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <AuthShell>
      {sent ? (
        <div className="auth-card">
          <div className="auth-head">
            <h1 className="auth-title">Check your email</h1>
            <p className="auth-sub">If that email exists, a reset link was sent.</p>
          </div>
          <Link to="/login" className="auth-submit" style={{ textAlign: 'center' }}>
            Back to login
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="auth-card">
          <div className="auth-head">
            <h1 className="auth-title">Forgot password</h1>
            <p className="auth-sub">Enter your email and we'll send a reset link.</p>
          </div>

          <label className="auth-field">
            <span>Email</span>
            <input
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="auth-input"
            />
          </label>

          {error && <p role="alert" className="auth-error">{error}</p>}

          <button type="submit" disabled={submitting} className="auth-submit">
            {submitting ? 'Sending…' : 'Send reset link'}
          </button>

          <Link to="/login" className="auth-toggle" style={{ textAlign: 'center' }}>
            Back to login
          </Link>
        </form>
      )}
    </AuthShell>
  );
};
