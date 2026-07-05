"""
Conversation Memory Service
---------------------------
Orchestrates high-level operations for conversation metadata, message logs, and
context builder queries. Integrates repositories and context window managers.
"""

import uuid
import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.core.memory.context_window import ContextWindowManager
from app.models.ai_conversation import AIConversation
from app.models.enums import AIModel, AIConversationStatus, AIMessageSender


class ConversationMemoryService:
    """
    Coordinates access to conversation memory components.
    """

    def __init__(self) -> None:
        self.context_window = ContextWindowManager()

    def get_active_context(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        system_prompt: str,
        workspace_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> List[Dict[str, str]]:
        """
        Retrieves active messages context for a conversation.
        """
        conversation_repo = ConversationRepository(db)
        message_repo = MessageRepository(db)

        conversation = conversation_repo.get_conversation_by_id(
            conversation_id=conversation_id,
            workspace_id=workspace_id,
            organization_id=organization_id,
        )
        if not conversation:
            return [{"role": "system", "content": system_prompt}]

        recent_messages = message_repo.get_recent_messages(conversation_id)
        return self.context_window.build_context(
            system_prompt=system_prompt,
            conversation=conversation,
            recent_messages=recent_messages,
        )

    def save_user_message(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        message: str,
        tokens_used: int,
    ) -> None:
        """
        Saves user query and updates conversation metrics immediately.
        """
        conversation_repo = ConversationRepository(db)
        message_repo = MessageRepository(db)

        conversation = conversation_repo.get_conversation_by_id_simple(conversation_id)
        if not conversation:
            return

        message_repo.create_message(
            conversation_id=conversation_id,
            sender_type=AIMessageSender.USER,
            message=message,
            tokens_used=tokens_used,
        )

        now = datetime.datetime.now(datetime.timezone.utc)
        conversation_repo.update_metrics(conversation, tokens_used, now)

    def save_ai_message(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        message: str,
        tokens_used: int,
        response_time_ms: Optional[int] = None,
    ) -> None:
        """
        Saves assistant response and updates conversation metrics immediately.
        """
        conversation_repo = ConversationRepository(db)
        message_repo = MessageRepository(db)

        conversation = conversation_repo.get_conversation_by_id_simple(conversation_id)
        if not conversation:
            return

        message_repo.create_message(
            conversation_id=conversation_id,
            sender_type=AIMessageSender.AI,
            message=message,
            tokens_used=tokens_used,
            response_time_ms=response_time_ms,
        )

        now = datetime.datetime.now(datetime.timezone.utc)
        conversation_repo.update_metrics(conversation, tokens_used, now)

    def save_exchange(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        user_message: str,
        ai_message: str,
        user_tokens: int,
        ai_tokens: int,
        response_time_ms: Optional[int] = None,
    ) -> None:
        """
        Saves user query and assistant response, and updates conversation metrics.
        """
        self.save_user_message(db, conversation_id, user_message, user_tokens)
        self.save_ai_message(
            db, conversation_id, ai_message, ai_tokens, response_time_ms
        )

    def create_conversation(
        self,
        db: Session,
        title: str,
        model_name: AIModel,
        workspace_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> AIConversation:
        conversation_repo = ConversationRepository(db)
        return conversation_repo.create_conversation(
            title=title,
            model_name=model_name,
            workspace_id=workspace_id,
            organization_id=organization_id,
            user_id=user_id,
        )

    def get_conversation_by_id(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        workspace_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> Optional[AIConversation]:
        conversation_repo = ConversationRepository(db)
        return conversation_repo.get_conversation_by_id(
            conversation_id=conversation_id,
            workspace_id=workspace_id,
            organization_id=organization_id,
        )

    def list_conversations(
        self,
        db: Session,
        workspace_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> List[AIConversation]:
        conversation_repo = ConversationRepository(db)
        return conversation_repo.list_conversations(
            workspace_id=workspace_id,
            organization_id=organization_id,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )

    def update_conversation(
        self,
        db: Session,
        conversation: AIConversation,
        title: Optional[str] = None,
        model_name: Optional[AIModel] = None,
        status: Optional[AIConversationStatus] = None,
        summary: Optional[str] = None,
    ) -> AIConversation:
        conversation_repo = ConversationRepository(db)
        return conversation_repo.update_conversation(
            conversation=conversation,
            title=title,
            model_name=model_name,
            status=status,
            summary=summary,
        )

    def soft_delete_conversation(
        self, db: Session, conversation: AIConversation
    ) -> None:
        conversation_repo = ConversationRepository(db)
        conversation_repo.soft_delete_conversation(conversation)

    def get_aggregate_stats(
        self,
        db: Session,
        workspace_id: uuid.UUID,
        organization_id: uuid.UUID,
    ) -> dict:
        conversation_repo = ConversationRepository(db)
        return conversation_repo.get_aggregate_stats(
            workspace_id=workspace_id,
            organization_id=organization_id,
        )
