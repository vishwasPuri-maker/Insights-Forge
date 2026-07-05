from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class SystemSetting(BaseModel):
    """
    Stores organization-level system settings.
    """

    __tablename__ = "system_settings"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    setting_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    setting_value: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="system_settings",
        lazy="selectin",
    )

    updater: Mapped["User"] = relationship(
        "User",
        back_populates="system_settings",
        foreign_keys=[updated_by],
        lazy="selectin",
    )
