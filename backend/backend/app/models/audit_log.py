from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import AuditAction

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User


class AuditLog(BaseModel):
    """
    Stores immutable audit events.
    """

    __tablename__ = "audit_logs"

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
    # Audit Information
    # ------------------------------------------------------------------

    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    action: Mapped[AuditAction] = mapped_column(
        Enum(
            AuditAction,
            name="audit_action_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    old_values: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    new_values: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    ip_address: Mapped[str | None] = mapped_column(
        String(45),
        nullable=True,
    )

    user_agent: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="audit_logs",
        lazy="selectin",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="audit_logs",
        foreign_keys=[user_id],
        lazy="selectin",
    )
