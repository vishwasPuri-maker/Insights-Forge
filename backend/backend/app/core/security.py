"""Password hashing and JWT token utilities.

Access tokens are short-lived (15 min) and carry the full tenant context the
API needs on every request: user id, organization, role and the caller's
workspace/sector. Refresh tokens are opaque-ish JWTs persisted in
``user_sessions`` so they can be revoked on logout.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


# ---------------------------------------------------------------------------
# Passwords
# ---------------------------------------------------------------------------
def _to_bytes(password: str) -> bytes:
    # bcrypt only considers the first 72 bytes; truncate explicitly so long
    # passwords hash/verify consistently instead of raising.
    return password.encode("utf-8")[:72]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_to_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_to_bytes(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------
def _encode(claims: dict[str, Any], expires_delta: timedelta, token_type: str) -> str:
    now = datetime.now(timezone.utc)
    to_encode = {
        **claims,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(
    *,
    user_id: uuid.UUID | str,
    organization_id: uuid.UUID | str,
    role: str,
    workspace_id: uuid.UUID | str,
    sector: str,
) -> str:
    """Access token carrying the full tenant context (Phase 2 requirement)."""
    claims = {
        "sub": str(user_id),
        "org_id": str(organization_id),
        "role": role,
        "workspace_id": str(workspace_id),
        "sector": sector,
    }
    return _encode(
        claims,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ACCESS_TOKEN_TYPE,
    )


def create_refresh_token(*, user_id: uuid.UUID | str) -> tuple[str, datetime]:
    """Return (token, expires_at). The token is stored in ``user_sessions``."""
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    token = _encode(
        {"sub": str(user_id)},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        REFRESH_TOKEN_TYPE,
    )
    return token, expires_at


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT. Returns claims or ``None`` if invalid/expired."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
