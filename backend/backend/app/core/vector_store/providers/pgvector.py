"""
app/core/vector_store/providers/pgvector.py
-------------------------------------------
PostgreSQL + pgvector implementation of the VectorStore interface.
Handles production-grade chunk vector indexing, similarity searching,
tenant isolation, statistics, and health checks.
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select, delete, func, text

from app.db.session import SessionLocal
from app.core.vector_store.provider import VectorStore
from app.models.vector_chunk import VectorChunk
from app.core.rag.exceptions import TenantIsolationViolationError

logger = logging.getLogger("pgvector-store")


class PgVectorStore(VectorStore):
    """
    PgVector provider implementation. Strictly PostgreSQL-only.
    """

    def __init__(self, collection_name: str) -> None:
        self.collection_name = collection_name

    def upsert(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        embeddings: List[List[float]],
        dimension: int,
    ) -> None:
        """
        Ingests document chunks and their embeddings into the PostgreSQL vector_chunks table.
        """
        if not texts:
            return

        # Validate that all incoming embeddings match the specified dimension
        for emb in embeddings:
            if len(emb) != dimension:
                raise ValueError(
                    f"Embedding dimension mismatch: expected {dimension}, got {len(emb)}"
                )

        with SessionLocal() as db:
            try:
                for doc, meta, cid, emb in zip(texts, metadatas, ids, embeddings):
                    # Resolve IDs and relationships
                    org_id = uuid.UUID(str(meta["organization_id"]))
                    ws_id = uuid.UUID(str(meta["workspace_id"]))
                    ds_id = uuid.UUID(str(meta["dataset_id"]))
                    rec_id = (
                        uuid.UUID(str(meta["record_id"]))
                        if meta.get("record_id")
                        else None
                    )
                    doc_id = (
                        uuid.UUID(str(meta["document_id"]))
                        if meta.get("document_id")
                        else None
                    )

                    # Prevent duplicates by purging any pre-existing chunk with this chunk ID / record ID combo
                    # Clean deterministic ID is generated as dsId_recId_chunkIndex in IndexingService
                    chunk_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(cid))

                    stmt = delete(VectorChunk).where(VectorChunk.id == chunk_uuid)
                    db.execute(stmt)

                    # Create new chunk row
                    chunk = VectorChunk(
                        id=chunk_uuid,
                        organization_id=org_id,
                        workspace_id=ws_id,
                        dataset_id=ds_id,
                        record_id=rec_id,
                        document_id=doc_id,
                        content=doc,
                        embedding=emb,
                        metadata_json=meta,
                    )
                    db.add(chunk)
                db.commit()
                logger.info(
                    f"Successfully upserted {len(texts)} vector chunks to pgvector."
                )
            except Exception as e:
                db.rollback()
                logger.error(f"Failed to upsert chunks in pgvector: {str(e)}")
                raise e

    def search(
        self,
        query_embedding: List[float],
        top_k: int,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Performs high-performance cosine similarity search with strict tenant and workspace isolation.
        """
        formatted_results = []
        with SessionLocal() as db:
            # Query ordered by cosine distance
            stmt = (
                select(
                    VectorChunk,
                    VectorChunk.embedding.cosine_distance(query_embedding).label(
                        "distance"
                    ),
                )
                .where(
                    VectorChunk.organization_id == organization_id,
                    VectorChunk.workspace_id == workspace_id,
                )
                .order_by(text("distance ASC"))
                .limit(top_k)
            )
            results = db.execute(stmt).all()

            for chunk, distance in results:
                # 1. Enforce cross-tenant isolation validation at retrieve time
                if (
                    chunk.organization_id != organization_id
                    or chunk.workspace_id != workspace_id
                ):
                    raise TenantIsolationViolationError(
                        f"Tenancy isolation violation: Chunk belongs to org={chunk.organization_id}, ws={chunk.workspace_id} "
                        f"but request was org={organization_id}, ws={workspace_id}."
                    )

                # 2. Calculate Cosine similarity from Cosine distance (similarity = 1.0 - distance)
                similarity = 1.0 - float(distance)
                if score_threshold is not None and similarity < score_threshold:
                    continue

                formatted_results.append(
                    {
                        "content": chunk.content,
                        "metadata": chunk.metadata_json,
                        "score": similarity,
                    }
                )

        return formatted_results

    def delete(self, dataset_id: uuid.UUID) -> None:
        """
        Removes all vector chunks linked to the given dataset_id.
        """
        with SessionLocal() as db:
            try:
                stmt = delete(VectorChunk).where(VectorChunk.dataset_id == dataset_id)
                db.execute(stmt)
                db.commit()
                logger.info(
                    f"Purged all vector chunks for dataset {dataset_id} from pgvector."
                )
            except Exception as e:
                db.rollback()
                logger.error(
                    f"Failed to delete chunks for dataset {dataset_id}: {str(e)}"
                )
                raise e

    def statistics(self) -> Dict[str, Any]:
        """
        Gathers count stats about pgvector indexed chunks.
        """
        with SessionLocal() as db:
            try:
                count_stmt = select(func.count()).select_from(VectorChunk)
                total_chunks = db.execute(count_stmt).scalar() or 0

                datasets_stmt = select(
                    func.count(func.distinct(VectorChunk.dataset_id))
                )
                total_datasets = db.execute(datasets_stmt).scalar() or 0

                return {
                    "provider": "pgvector",
                    "indexed_chunks": total_chunks,
                    "indexed_datasets": total_datasets,
                    "collection_name": self.collection_name,
                }
            except Exception as e:
                logger.error(f"Failed to compile pgvector stats: {str(e)}")
                return {"provider": "pgvector", "error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """
        Checks connection and verifies pgvector extension availability.
        """
        with SessionLocal() as db:
            try:
                # Querypg_extension to verify pgvector is loaded
                stmt = text("SELECT 1 FROM pg_extension WHERE extname = 'vector';")
                extension_exists = db.execute(stmt).scalar() is not None

                # Check simple query heartbeat
                db.execute(text("SELECT 1;"))

                return {
                    "provider": "pgvector",
                    "healthy": extension_exists,
                    "diagnostics": {
                        "extension_installed": extension_exists,
                        "connection_active": True,
                    },
                }
            except Exception as e:
                return {
                    "provider": "pgvector",
                    "healthy": False,
                    "diagnostics": {
                        "extension_installed": False,
                        "connection_active": False,
                        "error": str(e),
                    },
                }
