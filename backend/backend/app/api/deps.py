"""Shared FastAPI dependencies: DB session, current user, RBAC guards."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session, lazyload, noload

from app.core.errors import AppError
from app.core.security import ACCESS_TOKEN_TYPE, decode_token
from app.db.session import get_db
from app.models.enums import UserStatus
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    """Authenticated caller plus the tenant context carried by the JWT."""

    user: User
    organization_id: uuid.UUID
    role: str
    workspace_id: uuid.UUID
    sector: str

    @property
    def id(self) -> uuid.UUID:
        return self.user.id


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> CurrentUser:
    if credentials is None:
        raise AppError(401, "unauthorized", "Not authenticated")

    claims = decode_token(credentials.credentials)
    if claims is None or claims.get("type") != ACCESS_TOKEN_TYPE:
        raise AppError(401, "unauthorized", "Invalid or expired token")

    try:
        user_id = uuid.UUID(claims["sub"])
        org_id = uuid.UUID(claims["org_id"])
        workspace_id = uuid.UUID(claims["workspace_id"])
    except (KeyError, ValueError):
        raise AppError(401, "unauthorized", "Malformed token")

    # Load the user without its (all-selectin) relationships — this runs on
    # every request and we only need scalar fields here.
    user = db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            noload(User.organization),
            noload(User.user_roles),
            noload(User.sessions),
            noload(User.workspace_members),
            noload(User.datasets),
            noload(User.dataset_uploads),
            noload(User.analysis_jobs),
            noload(User.created_analysis_jobs),
            noload(User.updated_analysis_jobs),
            noload(User.ai_conversations),
            noload(User.report_exports),
            noload(User.notifications),
            noload(User.audit_logs),
            noload(User.system_settings)
        )
    ).scalar_one_or_none()
    if user is None or user.is_deleted or user.status != UserStatus.ACTIVE:
        raise AppError(401, "unauthorized", "User not found or inactive")

    return CurrentUser(
        user=user,
        organization_id=org_id,
        role=claims.get("role", "user"),
        workspace_id=workspace_id,
        sector=claims.get("sector", ""),
    )


def ensure_sector(current: CurrentUser, sector: str) -> uuid.UUID:
    """Resolve a path {sector} to the caller's workspace.

    One workspace == one sector, so the path sector must match the caller's
    workspace sector; otherwise there is no data for them under it.
    """
    if sector != current.sector:
        raise AppError(404, "not_found", f"No accessible data for sector '{sector}'")
    return current.workspace_id


def require_roles(*allowed: str):
    """Dependency factory enforcing that the caller holds one of ``allowed`` roles."""

    def _guard(current: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current.role not in allowed:
            raise AppError(403, "forbidden", "Insufficient permissions")
        return current

    return _guard
