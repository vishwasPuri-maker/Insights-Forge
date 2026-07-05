"""Authentication & tenant-bootstrap logic.

Signup provisions a full tenant: organization + the standard RBAC roles
(admin/manager/user) + a default workspace whose ``sector`` is the caller's
chosen sector + the first admin user. Tokens carry org/user/role/workspace/
sector so downstream sector endpoints can resolve the caller's workspace.
"""

from __future__ import annotations

import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, lazyload, noload

from app.core.config import settings
from app.services import email_service
from app.core.errors import AppError
from app.core.security import (
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.email_token import EmailToken
from app.models.enums import EmailTokenType, Sector
from app.models.organization import Organization
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.models.user_session import UserSession
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.schemas.auth import TokenResponse
import logging

logger = logging.getLogger(__name__)

# Standard org-scoped roles, highest privilege first.
DEFAULT_ROLES = ("admin", "manager", "user")


def _new_email_token(
    db: Session, user_id: uuid.UUID, token_type: EmailTokenType, ttl: timedelta
) -> str:
    token = secrets.token_urlsafe(32)
    db.add(
        EmailToken(
            user_id=user_id,
            token=token,
            token_type=token_type,
            expires_at=datetime.now(timezone.utc) + ttl,
        )
    )
    return token


def _consume_email_token(
    db: Session, token: str, token_type: EmailTokenType
) -> EmailToken:
    row = db.execute(
        select(EmailToken)
        .where(EmailToken.token == token, EmailToken.token_type == token_type)
        .options(lazyload("*"))
    ).scalar_one_or_none()
    if row is None or row.used_at is not None:
        raise AppError(400, "invalid_token", "Invalid or already-used token")
    expires_at = row.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        raise AppError(400, "expired_token", "Token has expired")
    row.used_at = datetime.now(timezone.utc)
    return row


def _slugify(name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "org"
    return f"{base}-{uuid.uuid4().hex[:8]}"


def resolve_role(db: Session, user: User) -> str:
    """The user's role name (defaults to 'user' if none assigned)."""
    row = (
        db.execute(
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user.id)
            .order_by(Role.name)
        )
        .scalars()
        .first()
    )
    return row or "user"


def resolve_workspace(db: Session, user: User) -> Workspace:
    """The user's primary workspace (their first membership)."""
    ws = (
        db.execute(
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user.id)
            .order_by(WorkspaceMember.joined_at)
            .options(
                noload(Workspace.organization),
                noload(Workspace.members),
                noload(Workspace.datasets),
                noload(Workspace.dashboards),
                noload(Workspace.reports),
                noload(Workspace.ai_conversations)
            )
        )
        .scalars()
        .first()
    )
    if ws is None:
        raise AppError(409, "no_workspace", "User has no workspace")
    return ws


def _issue_tokens(db: Session, user: User) -> TokenResponse:
    workspace = resolve_workspace(db, user)
    role = resolve_role(db, user)
    access = create_access_token(
        user_id=user.id,
        organization_id=user.organization_id,
        role=role,
        workspace_id=workspace.id,
        sector=(
            workspace.sector.value
            if hasattr(workspace.sector, "value")
            else str(workspace.sector)
        ),
    )
    refresh, expires_at = create_refresh_token(user_id=user.id)
    db.add(UserSession(user_id=user.id, refresh_token=refresh, expires_at=expires_at))
    db.flush()
    return TokenResponse(access_token=access, refresh_token=refresh)


def signup(
    db: Session,
    *,
    organization_name: str,
    email: str,
    password: str,
    sector: Sector,
) -> TokenResponse:
    existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing is not None:
        # In dev mode allow reusing existing account without email verification
        if not settings.AUTH_REQUIRE_EMAIL_VERIFICATION:
            # Ensure the user is marked as verified
            if not existing.is_verified:
                existing.is_verified = True
            tokens = _issue_tokens(db, existing)
            db.commit()
            return tokens
        raise AppError(409, "email_taken", "Email already registered")

    org = Organization(
        name=organization_name,
        slug=_slugify(organization_name),
        industry=sector.value,
    )
    db.add(org)
    db.flush()

    roles = {name: Role(organization_id=org.id, name=name) for name in DEFAULT_ROLES}
    db.add_all(roles.values())
    db.flush()

    user = User(
        organization_id=org.id,
        first_name="Admin",
        last_name=organization_name[:100],
        email=email,
        password_hash=hash_password(password),
        is_verified=not settings.AUTH_REQUIRE_EMAIL_VERIFICATION,  # set based on config
    )
    db.add(user)
    db.flush()

    db.add(UserRole(user_id=user.id, role_id=roles["admin"].id))

    workspace = Workspace(
        organization_id=org.id,
        name=f"{organization_name} Workspace",
        industry_type=sector.value,
        sector=sector,
        created_by=user.id,
    )
    db.add(workspace)
    db.flush()

    db.add(
        WorkspaceMember(workspace_id=workspace.id, user_id=user.id, member_role="admin")
    )
    db.flush()

    verify_token = _new_email_token(
        db,
        user.id,
        EmailTokenType.VERIFY_EMAIL,
        timedelta(hours=settings.EMAIL_VERIFY_TOKEN_EXPIRE_HOURS),
    )
    tokens = _issue_tokens(db, user)
    db.commit()

    if settings.AUTH_REQUIRE_EMAIL_VERIFICATION:
        sent = email_service.send_verification_email(email, verify_token)
        if not sent:
            logger.warning("Verification email failed to send to %s", email)
    return tokens


def login(db: Session, *, email: str, password: str) -> TokenResponse:
    user = db.execute(
        select(User)
        .where(User.email == email)
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
    if user is None or not verify_password(password, user.password_hash):
        raise AppError(401, "invalid_credentials", "Incorrect email or password")
    if not user.is_verified and settings.AUTH_REQUIRE_EMAIL_VERIFICATION:
        raise AppError(
            403, "email_not_verified", "Please verify your email before logging in"
        )

    user.last_login = datetime.now(timezone.utc)
    tokens = _issue_tokens(db, user)
    db.commit()
    return tokens


def verify_email(db: Session, *, token: str) -> None:
    row = _consume_email_token(db, token, EmailTokenType.VERIFY_EMAIL)
    user = db.get(User, row.user_id, options=[lazyload("*")])
    if user is None:
        raise AppError(400, "invalid_token", "Invalid token")
    user.is_verified = True
    db.commit()


def forgot_password(db: Session, *, email: str) -> None:
    """Always succeeds (does not leak whether the email exists)."""
    logger.debug("Forgot password request for email: %s", email)
    user = db.execute(
        select(User).where(User.email == email).options(lazyload("*"))
    ).scalar_one_or_none()
    if user is not None and not user.is_deleted:
        logger.info("User found, generating reset token for %s", email)
        reset_token = _new_email_token(
            db,
            user.id,
            EmailTokenType.PASSWORD_RESET,
            timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES),
        )
        db.commit()
        sent = email_service.send_password_reset_email(email, reset_token)
        if not sent:
            logger.warning("Password reset email failed to send to %s", email)
        else:
            logger.info("Password reset email sent to %s", email)
    else:
        logger.debug("Forgot password called with non‑existent or deleted account: %s", email)



def reset_password(db: Session, *, token: str, new_password: str) -> None:
    row = _consume_email_token(db, token, EmailTokenType.PASSWORD_RESET)
    user = db.get(User, row.user_id, options=[lazyload("*")])
    if user is None:
        raise AppError(400, "invalid_token", "Invalid token")
    user.password_hash = hash_password(new_password)
    # Revoke all existing sessions after a password reset.
    for session in db.execute(
        select(UserSession).where(UserSession.user_id == user.id)
    ).scalars():
        db.delete(session)
    db.commit()


def refresh(db: Session, *, refresh_token: str) -> TokenResponse:
    claims = decode_token(refresh_token)
    if claims is None or claims.get("type") != REFRESH_TOKEN_TYPE:
        raise AppError(401, "invalid_token", "Invalid refresh token")

    session = db.execute(
        select(UserSession)
        .where(UserSession.refresh_token == refresh_token)
        .options(noload(UserSession.user))
    ).scalar_one_or_none()
    if session is None:
        raise AppError(401, "invalid_token", "Session not found or revoked")

    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        raise AppError(401, "expired_token", "Refresh token expired")

    user = db.execute(
        select(User)
        .where(User.id == session.user_id)
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
    if user is None:
        raise AppError(401, "invalid_token", "User not found")

    # Rotate: drop the old session, issue a fresh access+refresh pair.
    db.delete(session)
    db.flush()
    tokens = _issue_tokens(db, user)
    db.commit()
    return tokens


def logout(db: Session, *, refresh_token: str) -> None:
    session = db.execute(
        select(UserSession)
        .where(UserSession.refresh_token == refresh_token)
        .options(noload(UserSession.user))
    ).scalar_one_or_none()
    if session is not None:
        db.delete(session)
        db.commit()
