"""
Summary Manager
---------------
Handles background tasks for generating concise conversation titles and
consolidating conversation history summaries using the LLM provider.
"""

import logging
import uuid
from typing import List
from app.db.session import SessionLocal
from app.core.llm.factory import LLMFactory
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.models.enums import AIMessageSender

logger = logging.getLogger("summary-manager")


class SummaryManager:
    """
    Coordinates title and summary generation calls to the LLM.
    """

    def __init__(self) -> None:
        pass

    def generate_title(
        self,
        conversation_id: uuid.UUID,
        user_query: str,
        ai_response: str,
    ) -> None:
        """
        Generates a short title (under 4 words) from the first query-response pair and persists it.
        """
        db = SessionLocal()
        try:
            llm_provider = LLMFactory.get_provider()

            prompt = (
                "You are an AI assistant helping to title a chat session.\n"
                "Review the following exchange and generate a title of 3-4 words that describes the topic.\n"
                "Do not include quotes, prefix, or explanation. Respond ONLY with the title.\n\n"
                f"User: {user_query}\n"
                f"Assistant: {ai_response}\n"
            )

            messages = [{"role": "user", "content": prompt}]
            res = llm_provider.generate(messages, temperature=0.1, max_tokens=15)

            if res.status == "success" and res.content:
                title = res.content.strip().strip('"').strip("'").strip()
                # Truncate to 100 characters if LLM over-generates
                if len(title) > 100:
                    title = title[:97] + "..."

                # Instantiate repository with fresh DB session
                conversation_repo = ConversationRepository(db)
                conversation = conversation_repo.get_conversation_by_id_simple(
                    conversation_id
                )
                if conversation:
                    conversation_repo.update_conversation(conversation, title=title)
                    db.commit()
                    logger.info(
                        f"Updated title for conversation {conversation_id}: '{title}'"
                    )
            else:
                logger.warning(
                    f"Failed to generate title for conversation {conversation_id}"
                )
        except Exception as e:
            logger.error(
                f"Error generating title for conversation {conversation_id}: {str(e)}"
            )
        finally:
            db.close()

    def consolidate_summary(
        self,
        conversation_id: uuid.UUID,
        old_summary: str | None,
        message_ids: List[uuid.UUID],
    ) -> None:
        """
        Consolidates previous summary and recent messages to create a new summary.
        Recent messages are re-loaded by ID to ensure session safety.
        """
        db = SessionLocal()
        try:
            llm_provider = LLMFactory.get_provider()
            conversation_repo = ConversationRepository(db)
            message_repo = MessageRepository(db)

            # Load messages chronologically using repository
            all_messages = message_repo.get_all_messages(conversation_id)
            # Filter to only the recent ones we specified by message_ids
            recent_messages = [m for m in all_messages if m.id in message_ids]

            # Format dialogue context
            dialogue_str = ""
            for m in recent_messages:
                role = "User" if m.sender_type == AIMessageSender.USER else "AI"
                dialogue_str += f"{role}: {m.message}\n"

            prompt = (
                "You are an AI assistant specialized in summarizing conversations.\n"
                "Review the conversation summary and the recent dialogue below, and generate a consolidated summary.\n"
                "Keep it concise, capturing major themes, KPI metrics, and strategic requests discussed.\n"
                "Respond ONLY with the consolidated summary.\n\n"
                f"Previous Summary: {old_summary or 'None'}\n\n"
                f"Recent Dialogue:\n{dialogue_str}\n"
            )

            messages = [{"role": "user", "content": prompt}]
            res = llm_provider.generate(messages, temperature=0.2, max_tokens=300)

            if res.status == "success" and res.content:
                new_summary = res.content.strip()
                conversation = conversation_repo.get_conversation_by_id_simple(
                    conversation_id
                )
                if conversation:
                    conversation_repo.update_conversation(
                        conversation, summary=new_summary
                    )
                    db.commit()
                    logger.info(
                        f"Consolidated summary for conversation {conversation_id}"
                    )
            else:
                logger.warning(
                    f"Failed to consolidate summary for conversation {conversation_id}"
                )
        except Exception as e:
            logger.error(
                f"Error consolidating summary for conversation {conversation_id}: {str(e)}"
            )
        finally:
            db.close()
