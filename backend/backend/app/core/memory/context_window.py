"""
Context Window Manager
----------------------
Manages the assembly and trimming of structured message contexts for LLM generation.
Standardizes prompt ordering and enforces strict token-budget limits.
"""

import logging
from typing import List, Dict
from app.core.config import settings
from app.models.ai_conversation import AIConversation
from app.models.ai_message import AIMessage
from app.models.enums import AIMessageSender

logger = logging.getLogger("context-window-manager")


class ContextWindowManager:
    """
    Assembles, slices, and formats the conversation prompt messages context.
    """

    def build_context(
        self,
        system_prompt: str,
        conversation: AIConversation,
        recent_messages: List[AIMessage],
    ) -> List[Dict[str, str]]:
        """
        Assembles prompt components in the required structural order.
        Returns a list of message dicts: [{"role": "...", "content": "..."}]
        """
        messages = []

        # 1. System Prompt (Identity, mission, safety, output format etc.)
        messages.append({"role": "system", "content": system_prompt})

        # 2. Conversation Summary (Retrieved from DB)
        if conversation.summary:
            messages.append(
                {
                    "role": "assistant",
                    "content": f"System Context — Summary of previous exchanges: {conversation.summary}",
                }
            )

        # 3. Recent Messages (Chronological sliding window)
        # Sliced using settings.MEMORY_RECENT_MESSAGES
        window_size = settings.MEMORY_RECENT_MESSAGES
        sliced_messages = (
            recent_messages[-window_size:]
            if len(recent_messages) > window_size
            else recent_messages
        )

        for msg in sliced_messages:
            role = "user" if msg.sender_type == AIMessageSender.USER else "assistant"
            messages.append({"role": role, "content": msg.message})

        # 4. [Placeholder] Semantic Memory
        # (Future long-term vector/embedding retrieval)
        # semantic_context = self._get_semantic_memory(conversation.id)

        # 5. [Placeholder] User Preferences
        # (Future personalization rules)
        # user_prefs = self._get_user_preferences(conversation.user_id)

        # 6. [Placeholder] Agent Memory
        # (Future routing history and chain-of-thought metrics)
        # agent_history = self._get_agent_routing_history(conversation.id)

        # 7. [Placeholder] Decision Memory
        # (Future decision cards related to this thread)
        # decision_links = self._get_decision_card_links(conversation.id)

        return messages

    def estimate_tokens(self, text: str) -> int:
        """
        Estimates the number of tokens in a text block using character division (chars / 4).
        """
        return len(text) // 4

    def estimate_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Estimates the total token count of a list of structured messages.
        """
        total = 0
        for m in messages:
            total += self.estimate_tokens(m.get("content", ""))
        return total
