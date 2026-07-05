from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import AIMessageSender

if TYPE_CHECKING:
    from app.models.ai_conversation import AIConversation


class AIMessage(BaseModel):
    """
    Represents a single message in an AI conversation.
    """

    __tablename__ = "ai_messages"

    # ------------------------------------------------------------------
    # Foreign Keys
    # ------------------------------------------------------------------

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_conversations.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------------------
    # Message Information
    # ------------------------------------------------------------------

    sender_type: Mapped[AIMessageSender] = mapped_column(
        Enum(
            AIMessageSender,
            name="ai_message_sender_enum",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    tokens_used: Mapped[int] = mapped_column(
        Integer,
        default=0,
        server_default="0",
        nullable=False,
    )

    response_time_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    conversation: Mapped["AIConversation"] = relationship(
        "AIConversation",
        back_populates="messages",
        lazy="selectin",
    )
