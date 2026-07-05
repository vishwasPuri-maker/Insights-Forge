"""
app/core/embedding/provider.py
------------------------------
Abstract base provider interface for generating text embeddings.
Allows provider-independent implementation of semantic search tasks.
"""

from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """
    Interface for embedding generators.
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """
        Returns the embedding vector dimension size.
        """
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Generates a vector embedding for a single query text.
        """
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generates vector embeddings for a list of documents in batch.
        """
        pass
