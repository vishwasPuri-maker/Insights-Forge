"""
app/core/rag/context_builder.py
------------------------------
Assembles vector search results into a clean, de-duplicated prompt context.
Respects a configurable maximum token budget using robust token estimation.
"""

import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.llm.token_counter import TokenCounter

logger = logging.getLogger("context-builder")


class ContextBuilder:
    """
    Assembles, de-duplicates, and limits search results for LLM prompt context injection.
    """

    def __init__(self, max_tokens: Optional[int] = None) -> None:
        self.max_tokens = (
            max_tokens if max_tokens is not None else settings.RAG_MAX_CONTEXT_TOKENS
        )

    def estimate_tokens(self, text: str) -> int:
        """
        Estimates the number of tokens in a string.
        """
        return TokenCounter.estimate_tokens(text)

    def build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Assembles search results into a structured prompt context block.
        Ensures ranking order is preserved, citations are formatted cleanly,
        and the total token size stays strictly within max_tokens.
        """
        if not search_results:
            return ""

        # 1. Preserving input ranking order (assumed sorted descending by score after fusion/rerank)
        # 2. De-duplicate by exact content to prevent duplicate text injection
        seen_contents = set()
        unique_results = []
        for res in search_results:
            content = res.get("content", "").strip()
            if not content:
                continue
            if content in seen_contents:
                continue
            seen_contents.add(content)
            unique_results.append(res)

        context_blocks = []
        sources = []
        accumulated_tokens = 0

        # Estimate overhead of the suffix "Sources:\n..."
        sources_header = "\n\nSources:\n"
        accumulated_tokens += TokenCounter.estimate_tokens(sources_header)

        for idx, res in enumerate(unique_results, 1):
            metadata = res.get("metadata", {})
            doc_id = (
                metadata.get("document_id")
                or metadata.get("source_file")
                or metadata.get("record_id")
                or "Unknown"
            )
            dataset_id = metadata.get("dataset_id") or "Unknown"
            score = res.get("score", 0.0)

            # Clean citation formatting
            citation = f"[Doc #{idx} - {doc_id} (Relevance: {score:.2f})]"

            block = f"--- Document Citation: {citation} ---\n" f"{res['content']}"

            block_tokens = TokenCounter.estimate_tokens(block)
            source_entry = f"- {doc_id} (Dataset: {dataset_id})"
            source_tokens = TokenCounter.estimate_tokens(source_entry + "\n")

            # Check if adding this block + its source reference fits within the remaining token budget
            if accumulated_tokens + block_tokens + source_tokens > self.max_tokens:
                logger.info(
                    f"Token budget reached. Skipping subsequent chunks. "
                    f"Accumulated tokens: {accumulated_tokens}, limit: {self.max_tokens}"
                )
                break

            context_blocks.append(block)
            sources.append(source_entry)
            accumulated_tokens += block_tokens + source_tokens

        if not context_blocks:
            return ""

        # Assemble the clean context with citations followed by the sources section
        main_context = "\n\n".join(context_blocks)
        sources_section = sources_header + "\n".join(sources)
        return main_context + sources_section
