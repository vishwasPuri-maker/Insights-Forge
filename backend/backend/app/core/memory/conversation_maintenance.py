"""
Conversation Maintenance
------------------------
Manages scheduling non-blocking background tasks for generating titles
and summaries in a separated pipeline, keeping user requests low-latency.
"""

import uuid
import logging
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from app.core.config import settings
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.core.memory.summary_manager import SummaryManager
from app.core.memory.context_window import ContextWindowManager

logger = logging.getLogger("conversation-maintenance")


class ConversationMaintenance:
    """
    Schedules background tasks for conversation summaries and titles.
    """

    def __init__(self) -> None:
        pass

    def run_maintenance(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        background_tasks: BackgroundTasks,
        user_query: str,
        ai_response: str,
    ) -> None:
        """
        Inspects conversation state and schedules title or summary updates if necessary.
        """
        conversation_repo = ConversationRepository(db)
        message_repo = MessageRepository(db)
        summary_manager = SummaryManager()
        context_window = ContextWindowManager()

        # Load conversation
        conversation = conversation_repo.get_conversation_by_id_simple(conversation_id)
        if not conversation:
            return

        # 1. Title Generation: Triggered when conversation has exactly 2 messages (User + AI turn)
        if conversation.total_messages == 2:
            logger.info(
                f"Scheduling title generation for conversation {conversation_id}"
            )
            background_tasks.add_task(
                summary_manager.generate_title,
                conversation_id,
                user_query,
                ai_response,
            )

        # 2. Summarization: Triggered when threshold is exceeded or token budget is reached.
        # Fetch slightly more than the threshold to detect if the threshold is exceeded.
        recent_messages = message_repo.get_recent_messages(
            conversation_id, limit=settings.MEMORY_SUMMARY_THRESHOLD + 5
        )

        # Calculate recent messages tokens
        recent_text = "".join([m.message for m in recent_messages])
        estimated_tokens = context_window.estimate_tokens(recent_text)

        if (
            len(recent_messages) > settings.MEMORY_SUMMARY_THRESHOLD
            or estimated_tokens > settings.MEMORY_MAX_CONTEXT_TOKENS
        ):
            logger.info(
                f"Scheduling summary consolidation for conversation {conversation_id}"
            )
            # Pass only serializable IDs and primitive values to the background task
            recent_ids = [m.id for m in recent_messages]
            background_tasks.add_task(
                summary_manager.consolidate_summary,
                conversation_id,
                conversation.summary,
                recent_ids,
            )
