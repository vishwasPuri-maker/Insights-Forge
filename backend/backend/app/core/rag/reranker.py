"""
app/core/rag/reranker.py
------------------------
Defines the Reranker abstraction and its concrete implementations.
Allows for post-retrieval re-scoring and sorting of document chunks.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class Reranker(ABC):
    """
    Abstract interface for document reranking models.
    """

    @abstractmethod
    def rerank(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes a query and a list of retrieval results and returns the re-ordered/re-scored list.
        """
        pass


class NoOpReranker(Reranker):
    """
    Pass-through reranker that returns results unchanged.
    """

    def rerank(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Returns retrieval results without modification.
        """
        return results


class DiversityReranker(Reranker):
    """
    Reranker that penalizes search results hailing from the same document/source
    to promote citation diversity in context prompt injection.
    """

    def __init__(self, penalty: Optional[float] = None) -> None:
        from app.core.config import settings

        self.penalty: float = (
            penalty if penalty is not None else settings.RAG_DIVERSITY_WEIGHT
        )

    def rerank(self, query: str, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Applies a multiplicative penalty to subsequent document hits to promote document diversity.
        """
        if not results:
            return []

        reranked = []
        source_counts: Dict[Any, int] = {}

        # Sort input results by their score descending
        sorted_results = sorted(
            results, key=lambda x: x.get("score", 0.0), reverse=True
        )

        for res in sorted_results:
            new_res = res.copy()
            meta = new_res.get("metadata", {})
            # Identify unique source key
            doc_id = (
                meta.get("document_id")
                or meta.get("source_file")
                or meta.get("record_id")
                or meta.get("dataset_id")
            )

            if doc_id:
                count = source_counts.get(doc_id, 0)
                # Multiplicative penalty: penalty ^ count
                new_res["score"] = new_res.get("score", 0.0) * (self.penalty**count)
                source_counts[doc_id] = count + 1

            reranked.append(new_res)

        # Re-sort based on updated diversity scores
        return sorted(reranked, key=lambda x: x.get("score", 0.0), reverse=True)
