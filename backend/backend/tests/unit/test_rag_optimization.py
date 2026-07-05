"""
tests/unit/test_rag_optimization.py
-----------------------------------
Unit tests for Milestone 4I: Production RAG Optimization & Retrieval Quality.
Covers QueryPreprocessor, ResultFusion, DiversityReranker, ContextBuilder,
MetricsRegistry, and Retriever end-to-end orchestration.
"""

import uuid
import pytest
import threading
from unittest.mock import patch

from app.core.rag.query_preprocessor import QueryPreprocessor
from app.core.rag.result_fusion import ResultFusion
from app.core.rag.reranker import DiversityReranker
from app.core.rag.context_builder import ContextBuilder
from app.core.rag.metrics import RAGMetricsRegistry
from app.core.rag.retriever import Retriever


# ======================================================================
# 1. QueryPreprocessor Tests
# ======================================================================


def test_query_preprocessor():
    preprocessor = QueryPreprocessor()

    # Unicode and whitespace normalization, lowercase, punctuation removal, duplicate token deduplication
    raw_query = "   The   Analytics!! Analytics query   query  "
    processed = preprocessor.preprocess_query(raw_query, remove_stopwords=False)
    # expected: "the analytics query" (deduped duplicate tokens and lowercase/punctuation cleaned)
    assert processed == "the analytics query"

    # Stop-word removal check
    processed_stopwords = preprocessor.preprocess_query(
        raw_query, remove_stopwords=True
    )
    # "the" is a stopword, so it should be stripped
    assert processed_stopwords == "analytics query"


# ======================================================================
# 2. ResultFusion Tests
# ======================================================================


def test_result_fusion():
    fusion = ResultFusion()

    org_id = uuid.uuid4()
    ws_id = uuid.uuid4()
    ds_id = uuid.uuid4()

    results = [
        {
            "content": "First semantic chunk text",
            "score": 0.9,
            "metadata": {
                "organization_id": org_id,
                "workspace_id": ws_id,
                "dataset_id": ds_id,
                "document_id": "doc1",
                "chunk_index": 0,
            },
        },
        {
            "content": "First semantic chunk text",  # Exact duplicate text
            "score": 0.85,
            "metadata": {
                "organization_id": org_id,
                "workspace_id": ws_id,
                "dataset_id": ds_id,
                "document_id": "doc1",
                "chunk_index": 0,
            },
        },
        {
            "content": "Second adjacent text chunk",  # Adjacent chunk index = 1
            "score": 0.8,
            "metadata": {
                "organization_id": org_id,
                "workspace_id": ws_id,
                "dataset_id": ds_id,
                "document_id": "doc1",
                "chunk_index": 1,
            },
        },
    ]

    fused = fusion.fuse_results(
        results, score_normalization="min-max", overlap_threshold=5
    )

    # Duplicate removed, adjacent merged: we should have exactly 1 fused chunk
    assert len(fused) == 1
    # Check that text is concatenated or merged
    assert "First semantic chunk text" in fused[0]["content"]
    assert "Second adjacent text chunk" in fused[0]["content"]
    # Max score preserved and normalized (since it's the only one left, min-max score is 1.0)
    assert fused[0]["score"] == 1.0


# ======================================================================
# 3. DiversityReranker Tests
# ======================================================================


def test_diversity_reranker():
    reranker = DiversityReranker(penalty=0.5)

    results = [
        {
            "content": "Doc A chunk 1",
            "score": 0.95,
            "metadata": {"document_id": "doc_a"},
        },
        {
            "content": "Doc A chunk 2",
            "score": 0.90,
            "metadata": {"document_id": "doc_a"},
        },  # Should be penalized: 0.90 * 0.5 = 0.45
        {
            "content": "Doc B chunk 1",
            "score": 0.80,
            "metadata": {"document_id": "doc_b"},
        },  # Will rise above Doc A chunk 2
    ]

    reranked = reranker.rerank("query", results)

    # Doc B chunk 1 should now be at position 1 (index 1)
    assert reranked[0]["metadata"]["document_id"] == "doc_a"
    assert reranked[1]["metadata"]["document_id"] == "doc_b"
    assert reranked[2]["metadata"]["document_id"] == "doc_a"
    assert reranked[2]["score"] == 0.45


# ======================================================================
# 4. ContextBuilder Tests
# ======================================================================


def test_context_builder():
    builder = ContextBuilder(max_tokens=80)

    results = [
        {
            "content": "Block A of text",
            "score": 0.9,
            "metadata": {"document_id": "doc1", "dataset_id": "ds1"},
        },
        {
            "content": "Block B of text",
            "score": 0.8,
            "metadata": {"document_id": "doc2", "dataset_id": "ds1"},
        },
        {
            "content": "Block C of text that is very long and will exceed the token budget limit",
            "score": 0.7,
            "metadata": {"document_id": "doc3", "dataset_id": "ds1"},
        },
    ]

    context = builder.build_context(results)

    # Verify citation formatting
    assert "[Doc #1 - doc1 (Relevance: 0.90)]" in context
    assert "Block A of text" in context
    assert "Block B of text" in context
    # Block C should have been skipped to respect token budget
    assert "Block C of text" not in context
    # Sources summary section exists
    assert "Sources:" in context
    assert "- doc1 (Dataset: ds1)" in context


# ======================================================================
# 5. MetricsRegistry Tests
# ======================================================================


def test_metrics_registry():
    registry = RAGMetricsRegistry()
    registry.reset()

    # Check concurrent writes
    threads = []

    def record_job(i):
        registry.record(
            query=f"query {i}",
            provider_name="sentence-transformers",
            vector_provider="chroma",
            preprocessing_latency=0.001,
            search_latency=0.010,
            fusion_latency=0.002,
            reranking_latency=0.003,
            context_latency=0.004,
            retrieved_chunks=3,
            returned_chunks=2,
            duplicate_removals=1,
            merged_chunks=0,
            discarded_chunks=1,
            average_similarity=0.8,
            minimum_similarity=0.7,
            maximum_similarity=0.9,
            context_token_count=100,
        )

    for i in range(10):
        t = threading.Thread(target=record_job, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    history = registry.history()
    assert len(history) == 10

    latest = registry.latest()
    assert latest is not None
    assert latest["vector_provider"] == "chroma"
    assert latest["total_retrieval_latency"] == pytest.approx(0.020)

    registry.reset()
    assert len(registry.history()) == 0


# ======================================================================
# 6. Retriever End-To-End Orchestration Tests
# ======================================================================


@patch("app.core.vector_store.providers.chroma.ChromaVectorStore.search")
def test_retriever_orchestration_flow(mock_search):
    org_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    mock_search.return_value = [
        {
            "content": "Deduplicated context block text",
            "score": 0.85,
            "metadata": {
                "document_id": "doc_x",
                "dataset_id": "ds_x",
                "chunk_index": 0,
            },
        }
    ]

    retriever = Retriever()
    registry = RAGMetricsRegistry()
    registry.reset()

    context = retriever.retrieve_and_build_context(
        query="Clean the query text!!", organization_id=org_id, workspace_id=ws_id
    )

    assert "Deduplicated context block text" in context
    assert registry.latest() is not None
    assert registry.latest()["retrieved_chunks"] == 1
    assert registry.latest()["returned_chunks"] == 1
