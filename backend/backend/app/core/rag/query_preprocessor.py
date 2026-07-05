"""
app/core/rag/query_preprocessor.py
----------------------------------
Stateless, thread-safe preprocessor component for normalizing, cleaning, and expanding
user RAG queries.
"""

import string
import unicodedata
from typing import Set, List


class QueryPreprocessor:
    """
    Stateless text preprocessing engine to prepare raw queries for embedding and retrieval.
    """

    DEFAULT_STOPWORDS: Set[str] = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "for",
        "with",
        "is",
        "was",
        "to",
        "of",
        "from",
        "by",
        "that",
        "this",
        "these",
        "those",
        "it",
        "its",
        "as",
        "are",
    }

    def preprocess_query(self, query: str, remove_stopwords: bool = True) -> str:
        """
        Executes query text cleaning pipelines: normalization, punctuation stripping,
        lowercase conversion, and stopword extraction.
        """
        if not query:
            return ""

        # 1. Unicode normalization (NFKC)
        normalized = unicodedata.normalize("NFKC", query)

        # 2. Lowercase
        normalized = normalized.lower()

        # 3. Punctuation cleanup
        table = str.maketrans(string.punctuation, " " * len(string.punctuation))
        normalized = normalized.translate(table)

        # 4. Whitespace splitting
        tokens = normalized.split()

        # 5. Stop-word removal
        if remove_stopwords:
            tokens = [t for t in tokens if t not in self.DEFAULT_STOPWORDS]

        # 6. Adjacent duplicate token removal
        deduplicated: List[str] = []
        for t in tokens:
            if not deduplicated or deduplicated[-1] != t:
                deduplicated.append(t)

        # 7. Expansion hook
        processed_query = " ".join(deduplicated)
        return self.expand_query(processed_query)

    def expand_query(self, query: str) -> str:
        """
        Hook for query expansion, synonym integration, or spelling corrections.
        Currently returns the query unmodified.
        """
        return query
