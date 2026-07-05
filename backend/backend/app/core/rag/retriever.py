"""
app/core/rag/retriever.py
-------------------------
Coordinates the end-to-end RAG retrieval pipeline: query embedding, vector search,
tenant isolation validation, reranking, and context assembly.
Tracks and logs detailed performance metrics without exposing sensitive content.
"""

import time
import uuid
import logging
from typing import Optional

from app.core.config import settings
from app.core.embedding.factory import EmbeddingFactory
from app.core.vector_store.factory import VectorStoreFactory
from app.core.rag.reranker import NoOpReranker, Reranker, DiversityReranker
from app.core.rag.context_builder import ContextBuilder
from app.core.rag.query_preprocessor import QueryPreprocessor
from app.core.rag.result_fusion import ResultFusion
from app.core.rag.metrics import RAGMetricsRegistry
from app.core.llm.token_counter import TokenCounter

logger = logging.getLogger("rag-retriever")


class Retriever:
    """
    Orchestrates search query retrieval, tenant checks, reranking, and prompt enrichment.
    """

    def __init__(self, reranker: Optional[Reranker] = None) -> None:
        self.embedding_provider = EmbeddingFactory.get_provider()
        self.vector_store = VectorStoreFactory.get_vector_store()

        # Resolve default reranker using diversity settings
        if reranker is not None:
            self.reranker = reranker
        elif settings.RAG_ENABLE_DIVERSITY:
            self.reranker = DiversityReranker()
        else:
            self.reranker = NoOpReranker()

        self.context_builder = ContextBuilder(
            max_tokens=settings.RAG_MAX_CONTEXT_TOKENS
        )
        self.preprocessor = QueryPreprocessor()
        self.fusion = ResultFusion()
        self.metrics_registry = RAGMetricsRegistry()

    def retrieve_and_build_context(
        self,
        query: str,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
    ) -> str:
        """
        Coordinates embedding, tenant-isolated vector search, reranking, and context assembly.
        Logs latency metrics and search stats without exposing sensitive data.
        """
        start_total = time.time()
        k = top_k if top_k is not None else settings.RAG_TOP_K
        threshold = (
            similarity_threshold
            if similarity_threshold is not None
            else settings.RAG_SIMILARITY_THRESHOLD
        )

        # 1. Query Preprocessing
        start_preprocess = time.time()
        if settings.RAG_ENABLE_PREPROCESSING:
            preprocessed_query = self.preprocessor.preprocess_query(
                query, remove_stopwords=settings.RAG_ENABLE_STOPWORDS
            )
        else:
            preprocessed_query = query
        preprocess_latency = time.time() - start_preprocess

        # 2. Embed Query
        start_embed = time.time()
        query_vector = self.embedding_provider.embed_query(preprocessed_query)
        embedding_latency = time.time() - start_embed

        # 3. Similarity search with tenant isolation
        start_search = time.time()
        raw_results = self.vector_store.search(
            query_embedding=query_vector,
            top_k=k,
            organization_id=organization_id,
            workspace_id=workspace_id,
            score_threshold=threshold,
        )
        search_latency = time.time() - start_search

        # 4. Result Fusion (de-duplicate & merge adjacent chunks)
        start_fusion = time.time()
        if settings.RAG_ENABLE_FUSION:
            seen_texts = set()
            dedup_list = []
            for r in raw_results:
                txt = r.get("content", "").strip()
                if txt and txt not in seen_texts:
                    seen_texts.add(txt)
                    dedup_list.append(r)

            duplicate_removals = len(raw_results) - len(dedup_list)
            fused_results = self.fusion.fuse_results(raw_results)
            merged_chunks = len(dedup_list) - len(fused_results)
        else:
            fused_results = raw_results.copy()
            duplicate_removals = 0
            merged_chunks = 0
        fusion_latency = time.time() - start_fusion

        # 5. Rerank results
        start_rerank = time.time()
        reranked_results = self.reranker.rerank(preprocessed_query, fused_results)
        reranking_latency = time.time() - start_rerank

        # 6. Build context
        start_context = time.time()
        context_string = self.context_builder.build_context(reranked_results)
        context_latency = time.time() - start_context

        # 7. Compute extra telemetry counts
        returned_chunks = context_string.count("--- Document Citation:")
        discarded_chunks = len(reranked_results) - returned_chunks

        scores = [res.get("score", 0.0) for res in reranked_results]
        avg_similarity = sum(scores) / len(scores) if scores else 0.0
        max_similarity = max(scores) if scores else 0.0
        min_similarity = min(scores) if scores else 0.0

        context_tokens = TokenCounter.estimate_tokens(context_string)

        # 8. Record metrics inside thread-safe singleton
        self.metrics_registry.record(
            query=query,
            provider_name=settings.EMBEDDING_PROVIDER,
            vector_provider=settings.VECTOR_PROVIDER,
            preprocessing_latency=preprocess_latency,
            search_latency=search_latency + embedding_latency,
            fusion_latency=fusion_latency,
            reranking_latency=reranking_latency,
            context_latency=context_latency,
            retrieved_chunks=len(raw_results),
            returned_chunks=returned_chunks,
            duplicate_removals=duplicate_removals,
            merged_chunks=merged_chunks,
            discarded_chunks=discarded_chunks,
            average_similarity=avg_similarity,
            minimum_similarity=min_similarity,
            maximum_similarity=max_similarity,
            context_token_count=context_tokens,
        )

        total_latency_ms = int((time.time() - start_total) * 1000)

        # Log detailed metrics
        logger.info(
            f"[RAG Retrieval Metrics] "
            f"query_len={len(query)} | "
            f"preprocess_latency_ms={int(preprocess_latency * 1000)} | "
            f"search_latency_ms={int((search_latency + embedding_latency) * 1000)} | "
            f"fusion_latency_ms={int(fusion_latency * 1000)} | "
            f"reranking_latency_ms={int(reranking_latency * 1000)} | "
            f"context_latency_ms={int(context_latency * 1000)} | "
            f"total_latency_ms={total_latency_ms} | "
            f"retrieved_chunks={len(raw_results)} | "
            f"returned_chunks={returned_chunks} | "
            f"workspace_id={workspace_id} | "
            f"organization_id={organization_id}"
        )

        return context_string
