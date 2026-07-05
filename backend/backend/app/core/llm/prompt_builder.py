"""
Structured Prompt Builder
-------------------------
A pure, stateless utility for assembling system directives, summaries,
message histories, RAG context, and queries into formatted message lists.
"""

from typing import List, Dict, Optional
from app.models.ai_message import AIMessage
from app.models.enums import AIMessageSender


class StructuredPromptBuilder:
    """
    Assembles prompt context structures deterministically without database I/O or configuration lookups.
    """

    @staticmethod
    def build_messages(
        system_prompt: str,
        summary: Optional[str],
        recent_messages: List[AIMessage],
        rag_context: Optional[str],
        query: str,
    ) -> List[Dict[str, str]]:
        """
        Assembles all prompt context components in structured order.
        Returns: List[Dict[str, str]] containing roles and content keys.
        """
        messages = []

        # 1. System Prompt + Safety instructions + RAG Context
        full_system = system_prompt
        if rag_context:
            full_system += f"\n\nRETRIEVED CONTEXT (RAG):\n{rag_context}"

        messages.append({"role": "system", "content": full_system})

        # 2. Conversation Summary
        if summary:
            messages.append(
                {
                    "role": "assistant",
                    "content": f"System Context — Summary of previous exchanges: {summary}",
                }
            )

        # 3. Chronological History Turns
        for msg in recent_messages:
            role = "user" if msg.sender_type == AIMessageSender.USER else "assistant"
            messages.append({"role": role, "content": msg.message})

        # 4. Final Query
        messages.append({"role": "user", "content": query})

        return messages
