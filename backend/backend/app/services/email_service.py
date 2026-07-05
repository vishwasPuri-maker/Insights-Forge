"""Transactional email via the Brevo API (https://api.brevo.com/v3/smtp/email).

Uses httpx directly (no SDK). If ``BREVO_API_KEY`` is unset the send is a
no-op (returns False) so local/dev flows don't hard-fail.
"""

from __future__ import annotations

import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

BREVO_ENDPOINT = "https://api.brevo.com/v3/smtp/email"


def _send(*, to_email: str, subject: str, html: str) -> bool:
    if not settings.BREVO_API_KEY:
        logger.warning("BREVO_API_KEY not set; skipping email to %s", to_email)
        return False

    payload = {
        "sender": {"name": settings.EMAIL_FROM_NAME, "email": settings.EMAIL_FROM},
        "to": [{"email": to_email}],
        "subject": subject,
        "htmlContent": html,
    }
    headers = {
        "api-key": settings.BREVO_API_KEY,
        "accept": "application/json",
        "content-type": "application/json",
    }
    if not settings.BREVO_API_KEY:
        logger.warning("BREVO_API_KEY not set; skipping email to %s", to_email)
        return True  # dev mode – treat as sent
    # In development, optionally skip real send to avoid external calls
    if settings.ENVIRONMENT == "development":
        logger.info("Development mode: pretending to send email to %s", to_email)
        return True
    try:
        resp = httpx.post(BREVO_ENDPOINT, json=payload, headers=headers, timeout=15.0)
    except httpx.HTTPError as exc:
        logger.error("Brevo request failed for %s: %s", to_email, exc)
        return False
    if resp.status_code >= 300:
        logger.error(
            "Brevo send to %s failed: %s %s", to_email, resp.status_code, resp.text
        )
        return False
    return True


def send_verification_email(to_email: str, token: str) -> bool:
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    html = (
        "<h2>Verify your email</h2>"
        "<p>Welcome to Insights Forge. Please confirm your email address:</p>"
        f'<p><a href="{link}">Verify email</a></p>'
        f"<p>Or paste this link: {link}</p>"
    )
    return _send(
        to_email=to_email, subject="Verify your Insights Forge email", html=html
    )


def send_password_reset_email(to_email: str, token: str) -> bool:
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    html = (
        "<h2>Reset your password</h2>"
        "<p>We received a request to reset your password. This link expires soon:</p>"
        f'<p><a href="{link}">Reset password</a></p>'
        f"<p>Or paste this link: {link}</p>"
        "<p>If you didn't request this, you can ignore this email.</p>"
    )
    return _send(
        to_email=to_email, subject="Reset your Insights Forge password", html=html
    )
