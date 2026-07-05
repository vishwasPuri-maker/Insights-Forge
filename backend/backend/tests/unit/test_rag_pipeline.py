"""
tests/unit/test_rag_pipeline.py
-------------------------------
Unit and integration tests for the RAG and retrieval pipeline.
Covers chunking, token budgeting, vector indexing, tenant isolation,
duplicate indexing prevention, deletion cleanup, and error validation.
"""

import uuid
import pytest
from typing import List

from app.core.config import settings
from app.core.rag.exceptions import (
    TenantIsolationViolationError,
    EmbeddingModelMismatchError,
)
from app.core.rag.chunking import RecordChunkingStrategy
from app.core.rag.reranker import NoOpReranker
from app.core.rag.context_builder import ContextBuilder
from app.core.embedding.provider import EmbeddingProvider
from app.core.vector_store.providers.chroma import ChromaVectorStore


# 1. Mock Embedding Provider for fast, reliable, offline-safe unit tests
class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 384) -> None:
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_query(self, text: str) -> List[float]:
        # Return a simple deterministic mock vector
        return [0.1] * self.dimension

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [[0.1] * self.dimension for _ in texts]


@pytest.fixture
def mock_embedding():
    return MockEmbeddingProvider()


@pytest.fixture
def temp_chroma_store(tmp_path):
    # Create a persistent Chroma store in a temporary test directory
    db_dir = str(tmp_path / "test_vector_db")
    collection_name = "test_collection_" + str(uuid.uuid4())[:8]
    return ChromaVectorStore(collection_name=collection_name, db_dir=db_dir)


def test_chunking_strategy():
    """
    Verifies that RecordChunkingStrategy splits text based on size and metadata parameters.
    """
    strategy = RecordChunkingStrategy(chunk_size=50, chunk_overlap=10)
    meta = {"dataset_id": "test_ds"}

    # Text smaller than chunk_size
    short_text = "Name: Retail Store | Location: NY"
    chunks = strategy.chunk_document(short_text, meta)
    assert len(chunks) == 1
    assert chunks[0]["content"] == short_text
    assert chunks[0]["metadata"]["chunk_index"] == 0
    assert chunks[0]["metadata"]["dataset_id"] == "test_ds"

    # Text larger than chunk_size
    long_text = "A" * 120
    chunks = strategy.chunk_document(long_text, meta)
    assert len(chunks) > 1
    assert chunks[0]["metadata"]["chunk_index"] == 0
    assert chunks[1]["metadata"]["chunk_index"] == 1


def test_noop_reranker():
    """
    Verifies that the NoOpReranker returns documents exactly as passed.
    """
    reranker = NoOpReranker()
    docs = [{"content": "Doc A", "score": 0.9}, {"content": "Doc B", "score": 0.8}]
    results = reranker.rerank("query", docs)
    assert results == docs


def test_context_builder_token_budgeting():
    """
    Verifies that ContextBuilder de-duplicates and truncates contexts to fit within token budgets.
    """
    # 1 token ~= 4 characters in character fallback
    # Let's set max_tokens to 70 tokens (~280 characters) to fit two blocks but exclude the third
    builder = ContextBuilder(max_tokens=70)

    search_results = [
        {
            "content": "Duplicate Text",
            "score": 0.95,
            "metadata": {"dataset_id": "ds_1", "source": "rec"},
        },
        {
            "content": "Duplicate Text",
            "score": 0.90,
            "metadata": {"dataset_id": "ds_1", "source": "rec"},
        },  # Duplicate
        {
            "content": "First unique content block",
            "score": 0.85,
            "metadata": {"dataset_id": "ds_1", "source": "rec"},
        },
        {
            "content": "Second unique block of text, which should push it over budget",
            "score": 0.80,
            "metadata": {"dataset_id": "ds_1", "source": "rec"},
        },
    ]

    context = builder.build_context(search_results)

    # Context should contain "Duplicate Text" and "First unique content block"
    assert "Duplicate Text" in context
    assert "First unique content block" in context
    # It should NOT contain the third block because it would exceed 100 chars (25 tokens)
    assert "Second unique block" not in context
    # Verify duplicates removed
    assert context.count("Duplicate Text") == 1


def test_tenant_isolation(temp_chroma_store, mock_embedding):
    """
    Verifies that similarity search enforces strict workspace and organization isolation.
    """
    org_a = uuid.uuid4()
    ws_a = uuid.uuid4()
    org_b = uuid.uuid4()
    ws_b = uuid.uuid4()
    ds_id = uuid.uuid4()

    # Index doc for Tenant A
    doc_a = "Tenant A business analytics report"
    meta_a = {
        "organization_id": str(org_a),
        "workspace_id": str(ws_a),
        "dataset_id": str(ds_id),
        "source": "dataset_record",
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_version": settings.EMBEDDING_VERSION,
        "schema_version": "1.0",
        "created_at": "2026-07-04",
    }

    # Index doc for Tenant B
    doc_b = "Tenant B agricultural yield stats"
    meta_b = {
        "organization_id": str(org_b),
        "workspace_id": str(ws_b),
        "dataset_id": str(ds_id),
        "source": "dataset_record",
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_version": settings.EMBEDDING_VERSION,
        "schema_version": "1.0",
        "created_at": "2026-07-04",
    }

    # Generate mock embeddings
    embeds = mock_embedding.embed_documents([doc_a, doc_b])

    temp_chroma_store.add_documents(
        texts=[doc_a, doc_b],
        metadatas=[meta_a, meta_b],
        ids=["id_a", "id_b"],
        embeddings=embeds,
    )

    # Search for Tenant A -> should only see doc_a
    results_a = temp_chroma_store.similarity_search(
        query_embedding=mock_embedding.embed_query("analytics"),
        top_k=5,
        organization_id=org_a,
        workspace_id=ws_a,
        score_threshold=0.0,
    )
    assert len(results_a) == 1
    assert results_a[0]["content"] == doc_a

    # Search for Tenant B -> should only see doc_b
    results_b = temp_chroma_store.similarity_search(
        query_embedding=mock_embedding.embed_query("agriculture"),
        top_k=5,
        organization_id=org_b,
        workspace_id=ws_b,
        score_threshold=0.0,
    )
    assert len(results_b) == 1
    assert results_b[0]["content"] == doc_b


def test_cross_tenant_isolation_violation(temp_chroma_store, mock_embedding):
    """
    Verifies that if Chroma returns a document belonging to another tenant due to internal
    mismatches, our validation raises TenantIsolationViolationError.
    """
    org_a = uuid.uuid4()
    ws_a = uuid.uuid4()
    org_b = uuid.uuid4()
    ws_b = uuid.uuid4()
    ds_id = uuid.uuid4()

    # Index doc for Tenant A, but we will intentionally query it using Tenant B's credentials
    # directly via Chroma collection (bypassing search filter) to test the post-retrieval validation.
    doc = "Tenant A private records"
    meta = {
        "organization_id": str(org_a),
        "workspace_id": str(ws_a),
        "dataset_id": str(ds_id),
        "source": "dataset_record",
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_version": settings.EMBEDDING_VERSION,
        "schema_version": "1.0",
        "created_at": "2026-07-04",
    }

    temp_chroma_store.add_documents(
        texts=[doc],
        metadatas=[meta],
        ids=["id_private"],
        embeddings=mock_embedding.embed_documents([doc]),
    )

    # We manually mock/hack search query where clause to return everything,
    # mimicking a situation where a filter failed or was bypassed.
    # In ChromaVectorStore, if we query and it yields doc with org_a, but we search under org_b:
    # Let's verify our validation check catches it!
    # To simulate this, we override collection.query return value temporarily
    original_query = temp_chroma_store.collection.query

    def mock_query(*args, **kwargs):
        # Ignore filter and return Tenant A's doc
        return {"documents": [[doc]], "metadatas": [[meta]], "distances": [[0.0]]}

    temp_chroma_store.collection.query = mock_query

    # Now execute similarity search for Tenant B. It should raise TenantIsolationViolationError!
    with pytest.raises(TenantIsolationViolationError) as exc_info:
        temp_chroma_store.similarity_search(
            query_embedding=mock_embedding.embed_query("test"),
            top_k=1,
            organization_id=org_b,
            workspace_id=ws_b,
        )
    assert "Tenancy violation" in str(exc_info.value)

    # Restore original query
    temp_chroma_store.collection.query = original_query


def test_embedding_model_refresh_validation(temp_chroma_store, mock_embedding):
    """
    Verifies that stored model mismatches raise EmbeddingModelMismatchError.
    """
    org_a = uuid.uuid4()
    ws_a = uuid.uuid4()
    ds_id = uuid.uuid4()

    # Add document with old embedding model name
    doc = "Legacy embedding text"
    meta = {
        "organization_id": str(org_a),
        "workspace_id": str(ws_a),
        "dataset_id": str(ds_id),
        "source": "dataset_record",
        "embedding_model": "old_model_name_123",
        "embedding_version": "v1",
        "schema_version": "1.0",
        "created_at": "2026-07-04",
    }

    temp_chroma_store.add_documents(
        texts=[doc],
        metadatas=[meta],
        ids=["id_legacy"],
        embeddings=mock_embedding.embed_documents([doc]),
    )

    # Perform query under current settings. It should fail because metadata model "old_model_name_123"
    # doesn't match settings.EMBEDDING_MODEL.
    with pytest.raises(EmbeddingModelMismatchError) as exc_info:
        temp_chroma_store.similarity_search(
            query_embedding=mock_embedding.embed_query("test"),
            top_k=1,
            organization_id=org_a,
            workspace_id=ws_a,
        )
    assert "Stored embedding model" in str(exc_info.value)


def test_duplicate_indexing_and_cleanup(temp_chroma_store, mock_embedding):
    """
    Verifies that re-indexing or deleting a dataset properly synchronizes and cleans up vector database entries.
    """
    org_a = uuid.uuid4()
    ws_a = uuid.uuid4()
    ds_id = uuid.uuid4()

    # Ingest document
    doc_1 = "Data row version 1"
    meta_1 = {
        "organization_id": str(org_a),
        "workspace_id": str(ws_a),
        "dataset_id": str(ds_id),
        "source": "dataset_record",
        "embedding_model": settings.EMBEDDING_MODEL,
        "embedding_version": settings.EMBEDDING_VERSION,
        "schema_version": "1.0",
        "created_at": "2026-07-04",
    }

    temp_chroma_store.add_documents(
        texts=[doc_1],
        metadatas=[meta_1],
        ids=["id_chunk_1"],
        embeddings=mock_embedding.embed_documents([doc_1]),
    )

    # Verify document exists
    results = temp_chroma_store.similarity_search(
        query_embedding=mock_embedding.embed_query("version 1"),
        top_k=5,
        organization_id=org_a,
        workspace_id=ws_a,
    )
    assert len(results) == 1

    # Simulate re-indexing (delete old dataset vectors first, then add updated version)
    temp_chroma_store.delete_dataset_documents(ds_id)

    # Confirm deletion
    results_after_delete = temp_chroma_store.similarity_search(
        query_embedding=mock_embedding.embed_query("version 1"),
        top_k=5,
        organization_id=org_a,
        workspace_id=ws_a,
    )
    assert len(results_after_delete) == 0

    # Ingest updated document
    doc_2 = "Data row version 2 (updated)"
    temp_chroma_store.add_documents(
        texts=[doc_2],
        metadatas=[meta_1],
        ids=["id_chunk_1"],
        embeddings=mock_embedding.embed_documents([doc_2]),
    )

    # Verify updated document exists
    results_updated = temp_chroma_store.similarity_search(
        query_embedding=mock_embedding.embed_query("version 2"),
        top_k=5,
        organization_id=org_a,
        workspace_id=ws_a,
    )
    assert len(results_updated) == 1
    assert results_updated[0]["content"] == doc_2
