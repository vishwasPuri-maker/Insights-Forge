"""
app/services/indexing_service.py
--------------------------------
Service for document and dataset record indexing. Handles serialization, chunking,
metadata decoration, batch embedding generation, and vector store updates.
"""

import uuid
import logging
from datetime import datetime, timezone

from app.core.config import settings
from app.core.embedding.factory import EmbeddingFactory
from app.core.vector_store.factory import VectorStoreFactory
from app.core.rag.chunking import RecordChunkingStrategy
from app.models.record import Record
from app.models.dataset import Dataset
from sqlalchemy.orm import Session, lazyload
from sqlalchemy import select

logger = logging.getLogger("indexing-service")


class IndexingService:
    """
    Handles indexing lifecycle (creation, deletion, and refresh/updates) of datasets in the vector store.
    """

    def __init__(self, db: Session) -> None:
        self.db = db
        self.embedding_provider = EmbeddingFactory.get_provider()
        self.vector_store = VectorStoreFactory.get_vector_store()
        self.chunking_strategy = RecordChunkingStrategy(
            chunk_size=settings.RAG_CHUNK_SIZE, chunk_overlap=settings.RAG_CHUNK_OVERLAP
        )

    def index_dataset(self, dataset_id: uuid.UUID) -> bool:
        """
        Loads all records for a dataset, serializes them, generates embeddings,
        and saves them to the vector store with frozen metadata.
        """
        logger.info(f"Initiating vector indexing for dataset: {dataset_id}")
        start_time = datetime.now(timezone.utc)

        # 1. Fetch Dataset & Records from database
        dataset = self.db.get(Dataset, dataset_id, options=[lazyload("*")])
        if not dataset:
            logger.error(f"Failed to find dataset {dataset_id} for indexing.")
            return False

        stmt = (
            select(Record)
            .where(Record.dataset_id == dataset_id, Record.is_deleted.is_(False))
            .options(lazyload("*"))
        )
        records = list(self.db.execute(stmt).scalars().all())

        if not records:
            logger.info(f"No records found to index for dataset: {dataset_id}")
            return True

        # 2. Serialize and chunk each record
        chunks_to_index = []
        for rec in records:
            # Construct a human-readable key-value representation
            record_text = " | ".join(
                f"{k}: {v}"
                for k, v in rec.data.items()
                if v is not None and str(v).strip() != ""
            )
            if not record_text.strip():
                continue

            # Build metadata matching frozen schema
            base_meta = {
                "workspace_id": str(dataset.workspace_id),
                "organization_id": str(dataset.organization_id),
                "dataset_id": str(dataset.id),
                "source": "dataset_record",
                "embedding_model": settings.EMBEDDING_MODEL,
                "embedding_version": settings.EMBEDDING_VERSION,
                "schema_version": "1.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "record_id": str(rec.id),
            }

            # Apply chunking strategy
            record_chunks = self.chunking_strategy.chunk_document(
                record_text, base_meta
            )

            # Enrich chunk metadata keys
            from app.core.llm.token_counter import TokenCounter

            for chunk in record_chunks:
                meta = chunk["metadata"]
                meta["document_id"] = str(dataset.id)
                meta["chunk_id"] = meta.get("chunk_index", 0)
                meta["page_number"] = (
                    int(rec.data.get("page_number", 1))
                    if rec.data.get("page_number")
                    else 1
                )
                meta["section"] = str(rec.data.get("section", "content"))
                meta["token_count"] = TokenCounter.estimate_tokens(chunk["content"])
                meta["source_file"] = dataset.file_name
                meta["created_at"] = datetime.now(timezone.utc).isoformat()

            chunks_to_index.extend(record_chunks)

        if not chunks_to_index:
            logger.warning("No valid text content extracted from records to index.")
            return True

        # 3. Generate embeddings in batches
        texts = [c["content"] for c in chunks_to_index]
        metadatas = [c["metadata"] for c in chunks_to_index]
        # Generate clean deterministic IDs for chunks to prevent duplicate inserts on re-indexing
        ids = [
            f"{c['metadata']['dataset_id']}_{c['metadata']['record_id']}_{c['metadata']['chunk_index']}"
            for c in chunks_to_index
        ]

        start_embed = datetime.now(timezone.utc)
        embeddings = self.embedding_provider.embed_documents(texts)
        embed_latency_ms = int(
            (datetime.now(timezone.utc) - start_embed).total_seconds() * 1000
        )

        # 4. Ingest into Vector Store
        self.vector_store.upsert(
            texts=texts,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings,
            dimension=self.embedding_provider.dimension,
        )

        total_latency = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(
            f"[Indexing Metrics] dataset_id={dataset_id} | "
            f"chunks_count={len(chunks_to_index)} | "
            f"embed_time_ms={embed_latency_ms} | "
            f"total_latency_sec={total_latency:.2f}"
        )
        return True

    def delete_dataset_index(self, dataset_id: uuid.UUID) -> None:
        """
        Deletes all vector embeddings associated with a dataset to sync deletions.
        """
        logger.info(f"Purging vector index for dataset: {dataset_id}")
        self.vector_store.delete(dataset_id)
