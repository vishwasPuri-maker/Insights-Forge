"""
app/core/vector_store/provider.py
---------------------------------
Abstract base interface class for vector database operations, enabling decoupled,
provider-agnostic implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import uuid


class VectorStore(ABC):
    """
    Abstract Interface for Vector database operations.
    """

    @abstractmethod
    def upsert(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        embeddings: List[List[float]],
        dimension: int,
    ) -> None:
        """
        Ingests document chunks and their embeddings into the vector store.
        """
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Performs similarity search with strict tenant and workspace boundaries.
        Returns a list of dicts: {"content": str, "metadata": dict, "score": float}
        """
        pass

    @abstractmethod
    def delete(self, dataset_id: uuid.UUID) -> None:
        """
        Deletes all documents associated with a specific dataset.
        """
        pass

    @abstractmethod
    def statistics(self) -> Dict[str, Any]:
        """
        Returns statistical metrics about the vector store index.
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Checks connection status and functional health of the vector database.
        """
        pass

    def similarity_search(
        self,
        query_embedding: List[float],
        top_k: int,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Backwards compatibility wrapper delegating to search.
        """
        return self.search(
            query_embedding=query_embedding,
            top_k=top_k,
            organization_id=organization_id,
            workspace_id=workspace_id,
            score_threshold=score_threshold,
        )

    def add_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        embeddings: Optional[List[List[float]]] = None,
    ) -> None:
        """
        Backwards compatibility alias for upsert.
        """
        if embeddings:
            dim = len(embeddings[0])
        else:
            from app.core.embedding.factory import EmbeddingFactory

            dim = EmbeddingFactory.get_provider().dimension
            embeddings = [[0.0] * dim for _ in texts]

        self.upsert(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings,
            dimension=dim,
        )

    def delete_dataset_documents(self, dataset_id: uuid.UUID) -> None:
        """
        Backwards compatibility alias for delete.
        """
        self.delete(dataset_id=dataset_id)
