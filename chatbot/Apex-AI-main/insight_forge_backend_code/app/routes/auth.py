"""Auth routes: signup / login / refresh / logout.

Refresh tokens are recorded in the DB (by jti) so logout can revoke them and
refresh can reject already-revoked ones. Access tokens stay stateless.
"""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import jwt_handler
from app.auth.security import hash_password, verify_password
from app.database import get_db
from app.models import Organization, User, UserSession
from app.schemas import LoginRequest, RefreshRequest, SignupRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


def _issue_tokens(db: Session, user: User) -> TokenResponse:
    access = jwt_handler.create_access_token(
        user.organization_id, user.id, user.role, user.sector
    )
    jti = uuid.uuid4()
    refresh, expires_at = jwt_handler.create_refresh_token(user.organization_id, user.id, jti)
    db.add(
        UserSession(
            jti=jti,
            user_id=user.id,
            organization_id=user.organization_id,
            expires_at=expires_at,
        )
    )
    db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Create a new organization + its first (admin) user, and log them in."""
    existing = db.scalar(select(User).where(User.email == body.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "email_taken", "message": "email already registered"},
        )
    organization = Organization(name=body.organization_name)
    db.add(organization)
    db.flush()  # assign organization.id
    user = User(
        organization_id=organization.id,
        email=body.email,
        password_hash=hash_password(body.password),
        role="admin",
        sector=body.sector,
    )
    db.add(user)
    db.flush()
    return _issue_tokens(db, user)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == body.email))
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_credentials", "message": "invalid email or password"},
        )
    return _issue_tokens(db, user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Exchange a valid, non-revoked refresh token for a fresh token pair."""
    payload = jwt_handler.decode_token(body.refresh_token, expected_type="refresh")
    jti = uuid.UUID(payload["jti"])
    record = db.get(UserSession, jti)
    if record is None or record.revoked or record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_refresh", "message": "refresh token is not valid"},
        )
    # Rotate: revoke the used token, issue a new pair.
    record.revoked = True
    user = db.get(User, uuid.UUID(payload["sub"]))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_refresh", "message": "user no longer exists"},
        )
    return _issue_tokens(db, user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(body: RefreshRequest, db: Session = Depends(get_db)) -> None:
    """Revoke the given refresh token. Idempotent."""
    try:
        payload = jwt_handler.decode_token(body.refresh_token, expected_type="refresh")
    except HTTPException:
        return  # already invalid — nothing to revoke
    record = db.get(UserSession, uuid.UUID(payload["jti"]))
    if record is not None and not record.revoked:
        record.revoked = True
        db.commit()
