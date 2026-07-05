"""User management: GET /users, POST /users, DELETE /users/{id}.

Admin only. New users always belong to the caller's own organization (the
organization_id is taken from the caller's token, never from the request body,
so an admin can't create users in another org). Auth tables are not RLS-protected,
so queries filter by organization_id explicitly.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.auth.jwt_handler import TokenData, require_role
from app.auth.security import hash_password
from app.database import get_db
from app.models import User, UserSession
from app.schemas import UserCreate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserOut])
def list_users(
    current: TokenData = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> list[User]:
    return list(
        db.scalars(
            select(User)
            .where(User.organization_id == uuid.UUID(current.organization_id))
            .order_by(User.created_at)
        ).all()
    )


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreate,
    current: TokenData = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> User:
    org_id = uuid.UUID(current.organization_id)
    existing = db.scalar(
        select(User).where(User.organization_id == org_id, User.email == body.email)
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "email_taken", "message": "email already in this organization"},
        )
    user = User(
        organization_id=org_id,  # always the caller's org, never from the body
        email=body.email,
        password_hash=hash_password(body.password),
        role=body.role,
        sector=body.sector,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: uuid.UUID,
    current: TokenData = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> None:
    if str(user_id) == current.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "cannot_delete_self", "message": "you cannot delete your own account"},
        )
    user = db.scalar(
        select(User).where(
            User.id == user_id,
            User.organization_id == uuid.UUID(current.organization_id),
        )
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "user not found"},
        )
    # Remove the user's refresh-token sessions first (FK) before deleting them.
    db.execute(delete(UserSession).where(UserSession.user_id == user.id))
    db.delete(user)
    db.commit()
