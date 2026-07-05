"""
app/core/rag/chunking.py
------------------------
Defines the ChunkingStrategy abstraction and its concrete implementations,
including RecordChunkingStrategy for splitting serialized database records.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class ChunkingStrategy(ABC):
    """
    Abstract strategy class for document chunking.
    """

    @abstractmethod
    def chunk_document(
        self, content: str, metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Splits raw content into logical, sized document chunks.
        """
        pass


class RecordChunkingStrategy(ChunkingStrategy):
    """
    Chunking strategy optimized for serialized key-value record data.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self, content: str, metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Chunks the content string. If within chunk_size, keeps intact. Otherwise, uses RecursiveCharacterTextSplitter.
        """
        if not content.strip():
            return []

        # If length fits in single chunk, bypass splitter
        if len(content) <= self.chunk_size:
            chunk_meta = metadata.copy()
            chunk_meta["chunk_index"] = 0
            return [{"content": content, "metadata": chunk_meta}]

        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap
        )

        chunks = splitter.split_text(content)
        results = []
        for idx, chunk_text in enumerate(chunks):
            chunk_meta = metadata.copy()
            chunk_meta["chunk_index"] = idx
            results.append({"content": chunk_text, "metadata": chunk_meta})
        return results
