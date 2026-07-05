"""User schemas — frozen by contract (UserCreate, UserOut)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import Sector


class RoleName(str, Enum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: RoleName = RoleName.USER
    sector: Sector


class UserOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    email: EmailStr
    role: str
    sector: str
    created_at: datetime
