"""
app/core/rag/metrics.py
-----------------------
Thread-safe, in-memory singleton registry to record and analyze RAG performance telemetry.
"""

import hashlib
import time
import threading
from typing import List, Dict, Any, Optional
from app.core.config import settings


class RAGMetricsRegistry:
    """
    In-memory registry singleton that gathers metrics from individual RAG searches.
    """

    _instance: Optional["RAGMetricsRegistry"] = None
    _lock = threading.Lock()
    _history: List[Dict[str, Any]]
    _registry_lock: threading.Lock

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RAGMetricsRegistry, cls).__new__(cls)
                cls._instance._history = []
                cls._instance._registry_lock = threading.Lock()
            return cls._instance

    def record(
        self,
        query: str,
        provider_name: str,
        vector_provider: str,
        preprocessing_latency: float,
        search_latency: float,
        fusion_latency: float,
        reranking_latency: float,
        context_latency: float,
        retrieved_chunks: int,
        returned_chunks: int,
        duplicate_removals: int,
        merged_chunks: int,
        discarded_chunks: int,
        average_similarity: float,
        minimum_similarity: float,
        maximum_similarity: float,
        context_token_count: int,
    ) -> Dict[str, Any]:
        """
        Gathers and appends a single RAG transaction metrics dictionary.
        """
        query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest() if query else ""

        metrics = {
            "timestamp": time.time(),
            "query_hash": query_hash,
            "provider_name": provider_name,
            "vector_provider": vector_provider,
            "preprocessing_latency": preprocessing_latency,
            "search_latency": search_latency,
            "fusion_latency": fusion_latency,
            "reranking_latency": reranking_latency,
            "context_latency": context_latency,
            "total_retrieval_latency": (
                preprocessing_latency
                + search_latency
                + fusion_latency
                + reranking_latency
                + context_latency
            ),
            "retrieved_chunks": retrieved_chunks,
            "returned_chunks": returned_chunks,
            "duplicate_removals": duplicate_removals,
            "merged_chunks": merged_chunks,
            "discarded_chunks": discarded_chunks,
            "average_similarity": average_similarity,
            "minimum_similarity": minimum_similarity,
            "maximum_similarity": maximum_similarity,
            "context_token_count": context_token_count,
        }

        with self._registry_lock:
            self._history.append(metrics)
            max_size = settings.RAG_METRICS_HISTORY_SIZE
            if len(self._history) > max_size:
                self._history.pop(0)

        return metrics

    def latest(self) -> Optional[Dict[str, Any]]:
        """
        Returns the latest recorded RAG metrics payload or None.
        """
        with self._registry_lock:
            return self._history[-1] if self._history else None

    def history(self) -> List[Dict[str, Any]]:
        """
        Returns a list of all historically recorded RAG metrics payloads.
        """
        with self._registry_lock:
            return list(self._history)

    def reset(self) -> None:
        """
        Wipes all in-memory telemetry records.
        """
        with self._registry_lock:
            self._history.clear()
