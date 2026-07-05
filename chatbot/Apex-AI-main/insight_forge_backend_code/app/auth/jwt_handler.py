"""JWT creation/verification plus the shared auth dependency.

Access tokens are short-lived (15 min) and carry `organization_id`, `user_id`,
`role`, and `sector` (so every request knows the caller's sector without a
re-lookup). Refresh tokens are long-lived, carry a `jti`, and are tracked in the
DB so they can be revoked on logout. `get_current_user` is the FastAPI
dependency every protected route uses to pull the caller's identity off the token.
"""
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from app.config import settings

bearer_scheme = HTTPBearer(auto_error=False)


class TokenData(BaseModel):
    organization_id: str
    user_id: str
    role: str
    sector: str


def _encode(payload: dict, expires: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {**payload, "iat": now, "exp": now + expires}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(organization_id: str, user_id: str, role: str, sector: str) -> str:
    return _encode(
        {
            "type": "access",
            "organization_id": str(organization_id),
            "sub": str(user_id),
            "role": role,
            "sector": sector,
        },
        timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(
    organization_id: str, user_id: str, jti: uuid.UUID
) -> tuple[str, datetime]:
    """Return (token, expires_at) so the caller can persist the jti for revocation."""
    expires = timedelta(days=settings.refresh_token_expire_days)
    token = _encode(
        {
            "type": "refresh",
            "organization_id": str(organization_id),
            "sub": str(user_id),
            "jti": str(jti),
        },
        expires,
    )
    return token, datetime.now(timezone.utc) + expires


def decode_token(token: str, expected_type: str) -> dict:
    """Decode and validate a token, raising 401 on any problem."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        raise _unauthorized("invalid or expired token")
    if payload.get("type") != expected_type:
        raise _unauthorized("wrong token type")
    return payload


def _unauthorized(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "unauthorized", "message": message},
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> TokenData:
    """Shared dependency: verify the access token, return the caller's identity."""
    if credentials is None:
        raise _unauthorized("missing bearer token")
    payload = decode_token(credentials.credentials, expected_type="access")
    return TokenData(
        organization_id=payload["organization_id"],
        user_id=payload["sub"],
        role=payload["role"],
        sector=payload["sector"],
    )


def require_role(*allowed: str):
    """Dependency factory enforcing RBAC: user < manager < admin."""

    def _guard(current: TokenData = Depends(get_current_user)) -> TokenData:
        if current.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "forbidden", "message": "insufficient role"},
            )
        return current

    return _guard
