"""
tests/unit/test_vector_pipeline.py
----------------------------------
Unit tests for Milestone 4H: Production Vector Database & Embedding Pipeline.
Covers Factories, Ollama/OpenAI mocked providers, PgVectorStore mocks, ChromaVectorStore,
metadata preservation, dimension validation, and health checks.
"""

import uuid
import pytest
from unittest.mock import Mock, MagicMock, patch

from app.core.config import settings
from app.core.embedding.factory import EmbeddingFactory
from app.core.embedding.providers.sentence_transformer import (
    SentenceTransformerProvider,
)
from app.core.embedding.providers.ollama import OllamaEmbeddingProvider
from app.core.embedding.providers.openai import OpenAIEmbeddingProvider

from app.core.vector_store.factory import VectorStoreFactory
from app.core.vector_store.providers.chroma import ChromaVectorStore
from app.core.vector_store.providers.pgvector import PgVectorStore


# ======================================================================
# 1. Embedding Provider & Factory Tests
# ======================================================================


def test_embedding_factory_resolution():
    """
    Verifies that the factory resolves providers correctly based on configuration.
    """
    with patch.object(settings, "EMBEDDING_PROVIDER", "sentence-transformers"):
        provider = EmbeddingFactory.get_provider()
        assert isinstance(provider, SentenceTransformerProvider)
        assert provider.dimension == 384

    with patch.object(settings, "EMBEDDING_PROVIDER", "ollama"):
        # Mock probe request
        with patch.object(
            OllamaEmbeddingProvider, "embed_query", return_value=[0.1] * 100
        ):
            provider = EmbeddingFactory.get_provider()
            assert isinstance(provider, OllamaEmbeddingProvider)
            assert provider.dimension == 100

    with patch.object(settings, "EMBEDDING_PROVIDER", "openai"):
        provider = EmbeddingFactory.get_provider()
        assert isinstance(provider, OpenAIEmbeddingProvider)
        assert provider.dimension == 1536


@patch("httpx.Client.post")
def test_ollama_provider_embeddings(mock_post):
    """
    Verifies Ollama provider payload format and parsing.
    """
    # Mock /api/embeddings response
    mock_post.return_value = Mock(
        status_code=200, json=lambda: {"embedding": [0.25] * 384}
    )

    provider = OllamaEmbeddingProvider(
        model_name="nomic-embed-text", base_url="http://localhost:11434"
    )
    assert provider.dimension == 384

    # Verify single query embedding
    vec = provider.embed_query("analytics query")
    assert len(vec) == 384
    assert vec[0] == 0.25

    # Verify batch document embeddings using /api/embed mock fallback
    mock_post.return_value = Mock(
        status_code=200, json=lambda: {"embeddings": [[0.5] * 384, [0.6] * 384]}
    )
    docs = provider.embed_documents(["doc 1", "doc 2"])
    assert len(docs) == 2
    assert docs[0][0] == 0.5
    assert docs[1][0] == 0.6


@patch("httpx.Client.post")
def test_openai_provider_embeddings(mock_post):
    """
    Verifies OpenAI provider payload mapping and sorting by index.
    """
    mock_post.return_value = Mock(
        status_code=200,
        json=lambda: {
            "data": [
                {"embedding": [0.1] * 1536, "index": 0},
                {"embedding": [0.2] * 1536, "index": 1},
            ]
        },
    )

    provider = OpenAIEmbeddingProvider(
        model_name="text-embedding-3-small", api_key="sk-test"
    )
    assert provider.dimension == 1536

    docs = provider.embed_documents(["first", "second"])
    assert len(docs) == 2
    assert docs[0][0] == 0.1
    assert docs[1][0] == 0.2


# ======================================================================
# 2. Vector Store Factory & Mismatch Validation Tests
# ======================================================================


def test_vector_store_factory_resolution():
    """
    Verifies VectorStoreFactory cases mapping.
    """
    with patch.object(settings, "VECTOR_PROVIDER", "chroma"):
        store = VectorStoreFactory.get_vector_store()
        assert isinstance(store, ChromaVectorStore)

    with patch.object(settings, "VECTOR_PROVIDER", "pgvector"):
        store = VectorStoreFactory.get_vector_store()
        assert isinstance(store, PgVectorStore)


def test_chroma_dimension_mismatch_validation(tmp_path):
    """
    Asserts ChromaVectorStore raises ValueError on dimension mismatch.
    """
    db_dir = str(tmp_path / "chroma_test")
    store = ChromaVectorStore(collection_name="test_col", db_dir=db_dir)

    with pytest.raises(ValueError) as exc:
        store.upsert(
            texts=["short text"],
            metadatas=[{"org": "test"}],
            ids=["id1"],
            embeddings=[[0.1] * 128],
            dimension=256,
        )
    assert "dimension mismatch" in str(exc.value)


# ======================================================================
# 3. PgVectorStore DB Operations Tests (Mocked DB Session)
# ======================================================================


@patch("app.core.vector_store.providers.pgvector.SessionLocal")
def test_pgvector_upsert_validation_and_inserts(mock_session_local):
    """
    Checks that PgVectorStore validates dimensions, wipes duplicates,
    and inserts VectorChunk instances correctly.
    """
    mock_db = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db

    store = PgVectorStore(collection_name="pg_col")

    # Mismatch dimension validation
    with pytest.raises(ValueError):
        store.upsert(
            texts=["doc"],
            metadatas=[{"organization_id": uuid.uuid4(), "workspace_id": uuid.uuid4()}],
            ids=["cid"],
            embeddings=[[0.1] * 10],
            dimension=20,
        )

    # Success path
    org_id = uuid.uuid4()
    ws_id = uuid.uuid4()
    ds_id = uuid.uuid4()
    rec_id = uuid.uuid4()

    store.upsert(
        texts=["Valid semantic chunk content"],
        metadatas=[
            {
                "organization_id": org_id,
                "workspace_id": ws_id,
                "dataset_id": ds_id,
                "record_id": rec_id,
                "chunk_index": 0,
            }
        ],
        ids=["chunk_a"],
        embeddings=[[0.5] * 384],
        dimension=384,
    )

    assert mock_db.execute.called
    assert mock_db.add.called
    assert mock_db.commit.called


@patch("app.core.vector_store.providers.pgvector.SessionLocal")
def test_pgvector_search_isolation_and_scores(mock_session_local):
    """
    Verifies that PgVectorStore queries cosine distance correctly
    and enforces runtime tenant isolation filters.
    """
    mock_db = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db

    org_id = uuid.uuid4()
    ws_id = uuid.uuid4()

    # Define mock chunk record returned by execute()
    mock_chunk = MagicMock()
    mock_chunk.organization_id = org_id
    mock_chunk.workspace_id = ws_id
    mock_chunk.content = "Isolated data content"
    mock_chunk.metadata_json = {"meta": "val"}

    # Mock execute return values: tuple(chunk, distance)
    # Cosine distance = 0.2 means similarity = 0.8
    mock_db.execute.return_value.all.return_value = [(mock_chunk, 0.2)]

    store = PgVectorStore(collection_name="pg_col")
    results = store.search(
        query_embedding=[0.1] * 384,
        top_k=5,
        organization_id=org_id,
        workspace_id=ws_id,
        score_threshold=0.5,
    )

    assert len(results) == 1
    assert results[0]["content"] == "Isolated data content"
    assert results[0]["score"] == 0.8
    assert results[0]["metadata"] == {"meta": "val"}

    # Test isolation violation crash
    mock_chunk.organization_id = uuid.uuid4()  # different organization
    with pytest.raises(Exception) as exc:
        store.search(
            query_embedding=[0.1] * 384,
            top_k=5,
            organization_id=org_id,
            workspace_id=ws_id,
        )
    assert "Tenancy isolation violation" in str(exc.value)


@patch("app.core.vector_store.providers.pgvector.SessionLocal")
def test_pgvector_health_and_statistics(mock_session_local):
    """
    Verifies PgVectorStore health diagnostics and statistics compile.
    """
    mock_db = MagicMock()
    mock_session_local.return_value.__enter__.return_value = mock_db

    # Setup database stats results
    mock_db.execute.return_value.scalar.side_effect = [150, 2]  # 150 chunks, 2 datasets

    store = PgVectorStore("pg_col")
    stats = store.statistics()
    assert stats["indexed_chunks"] == 150
    assert stats["indexed_datasets"] == 2

    # Setup extension check: return True/1 for pgvector loaded
    mock_db.execute.return_value.scalar.side_effect = [True, 1]
    health = store.health_check()
    assert health["healthy"] is True
    assert health["diagnostics"]["extension_installed"] is True
