"""User management endpoints (org-scoped). Create/delete are admin-only."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, lazyload

from app.api.deps import CurrentUser, get_current_user, require_roles
from app.core.errors import AppError
from app.core.security import hash_password
from app.db.session import get_db
from app.models.enums import Sector
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember
from app.schemas.user import UserCreate, UserOut
from app.services.auth_service import resolve_role, resolve_workspace

router = APIRouter(prefix="/users", tags=["Users"])


def to_out(db: Session, user: User) -> UserOut:
    workspace = resolve_workspace(db, user)
    return UserOut(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        role=resolve_role(db, user),
        sector=workspace.sector.value,
        created_at=user.created_at,
    )


def _role_for(db: Session, org_id: uuid.UUID, name: str) -> Role:
    role = db.execute(
        select(Role)
        .where(Role.organization_id == org_id, Role.name == name)
        .options(lazyload("*"))
    ).scalar_one_or_none()
    if role is None:
        role = Role(organization_id=org_id, name=name)
        db.add(role)
        db.flush()
    return role


def _workspace_for_sector(
    db: Session, org_id: uuid.UUID, sector: Sector, created_by: uuid.UUID
) -> Workspace:
    ws = (
        db.execute(
            select(Workspace)
            .where(Workspace.organization_id == org_id, Workspace.sector == sector)
            .options(lazyload("*"))
        )
        .scalars()
        .first()
    )
    if ws is None:
        ws = Workspace(
            organization_id=org_id,
            name=f"{sector.value.title()} Workspace",
            industry_type=sector.value,
            sector=sector,
            created_by=created_by,
        )
        db.add(ws)
        db.flush()
    return ws


@router.get("", response_model=list[UserOut])
def list_users(
    current: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[UserOut]:
    stmt = (
        select(User)
        .where(
            User.organization_id == current.organization_id,
            User.is_deleted.is_(False),
        )
        .order_by(User.created_at)
    )
    return [to_out(db, u) for u in db.execute(stmt).scalars().all()]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    current: CurrentUser = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> UserOut:
    exists = db.execute(
        select(User).where(User.email == payload.email).options(lazyload("*"))
    ).scalar_one_or_none()
    if exists is not None:
        raise AppError(409, "email_taken", "Email already registered")

    org_id = current.organization_id
    user = User(
        organization_id=org_id,
        first_name=payload.email.split("@")[0][:100],
        last_name="",
        email=payload.email,
        password_hash=hash_password(payload.password),
        is_verified=True,
    )
    db.add(user)
    db.flush()

    db.add(
        UserRole(user_id=user.id, role_id=_role_for(db, org_id, payload.role.value).id)
    )
    workspace = _workspace_for_sector(db, org_id, payload.sector, current.id)
    db.add(
        WorkspaceMember(
            workspace_id=workspace.id, user_id=user.id, member_role=payload.role.value
        )
    )
    db.commit()
    return to_out(db, user)


@router.delete(
    "/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
def delete_user(
    user_id: uuid.UUID,
    current: CurrentUser = Depends(require_roles("admin")),
    db: Session = Depends(get_db),
) -> Response:
    user = db.get(User, user_id, options=[lazyload("*")])
    if (
        user is None
        or user.is_deleted
        or user.organization_id != current.organization_id
    ):
        raise AppError(404, "not_found", "User not found")
    if user.id == current.id:
        raise AppError(409, "cannot_delete_self", "You cannot delete your own account")
    user.is_deleted = True
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
