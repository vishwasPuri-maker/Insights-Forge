from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.audit import AuditMixin
from app.models.base import BaseModel
from app.models.enums import (
    NotificationChannel,
    NotificationStatus,
    NotificationType,
)

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class Notification(BaseModel, AuditMixin):
    """
    Represents a system notification delivered to a user.
    """

    __tablename__ = "notifications"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Notification Information
    # ------------------------------------------------------------------

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    notification_type: Mapped[NotificationType] = mapped_column(
        Enum(
            NotificationType,
            name="notification_type_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    delivery_channel: Mapped[NotificationChannel] = mapped_column(
        Enum(
            NotificationChannel,
            name="notification_channel_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[NotificationStatus] = mapped_column(
        Enum(
            NotificationStatus,
            name="notification_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=NotificationStatus.ACTIVE,
        server_default=NotificationStatus.ACTIVE.value,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="notifications",
        lazy="selectin",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
        foreign_keys=[user_id],
        lazy="selectin",
    )
