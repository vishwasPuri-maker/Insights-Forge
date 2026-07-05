from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.audit import AuditMixin
from app.models.base import BaseModel
from app.models.enums import (
    AIConversationStatus,
    AIModel,
)

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.workspace import Workspace
    from app.models.user import User
    from app.models.ai_message import AIMessage


class AIConversation(BaseModel, AuditMixin):
    """
    Represents an AI conversation within a workspace.
    """

    __tablename__ = "ai_conversations"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id"),
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
    # Conversation Information
    # ------------------------------------------------------------------

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    model_name: Mapped[AIModel] = mapped_column(
        Enum(
            AIModel,
            name="ai_model_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    status: Mapped[AIConversationStatus] = mapped_column(
        Enum(
            AIConversationStatus,
            name="ai_conversation_status_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=AIConversationStatus.ACTIVE,
        server_default=AIConversationStatus.ACTIVE.value,
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    total_messages: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    total_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    last_message_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    last_summary_at: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="ai_conversations",
        lazy="selectin",
    )

    workspace: Mapped["Workspace"] = relationship(
        "Workspace",
        back_populates="ai_conversations",
        lazy="selectin",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="ai_conversations",
        foreign_keys=[user_id],
        lazy="selectin",
    )

    messages: Mapped[list["AIMessage"]] = relationship(
        "AIMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
