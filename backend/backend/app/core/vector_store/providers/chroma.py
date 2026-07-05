"""
app/core/vector_store/providers/chroma.py
-----------------------------------------
ChromaDB implementation of the VectorStore interface.
Enforces multi-tenancy bounds and embedding integrity constraints.
"""

import uuid
import logging
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.vector_store.provider import VectorStore
from app.core.rag.exceptions import (
    TenantIsolationViolationError,
    EmbeddingModelMismatchError,
)

logger = logging.getLogger("vector-store")


class ChromaVectorStore(VectorStore):
    """
    ChromaDB provider implementation.
    """

    def __init__(self, collection_name: str, db_dir: str) -> None:
        import chromadb

        self.client = chromadb.PersistentClient(path=db_dir)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def upsert(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str],
        embeddings: List[List[float]],
        dimension: int,
    ) -> None:
        """
        Ingests document chunks and their metadata into ChromaDB.
        """
        if not texts:
            return

        # Validate dimension size
        for emb in embeddings:
            if len(emb) != dimension:
                raise ValueError(
                    f"Embedding dimension mismatch: expected {dimension}, got {len(emb)}"
                )

        # Ensure metadata values conform to ChromaDB's accepted types (str, int, float, bool)
        sanitized_metadatas = []
        for meta in metadatas:
            sanitized = {}
            for k, v in meta.items():
                if isinstance(v, uuid.UUID):
                    sanitized[k] = str(v)
                elif isinstance(v, (str, int, float, bool)):
                    sanitized[k] = v
                else:
                    sanitized[k] = str(v)
            sanitized_metadatas.append(sanitized)

        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=sanitized_metadatas,
            ids=ids,
        )
        logger.info(f"Successfully added {len(texts)} documents to vector store.")

    def search(
        self,
        query_embedding: List[float],
        top_k: int,
        organization_id: uuid.UUID,
        workspace_id: uuid.UUID,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Searches ChromaDB while validating isolation and model consistency.
        """
        where_filter = {
            "$and": [
                {"organization_id": str(organization_id)},
                {"workspace_id": str(workspace_id)},
            ]
        }

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = (
                results["metadatas"][0] if results["metadatas"] else [None] * len(docs)
            )
            dists = (
                results["distances"][0] if results["distances"] else [0.0] * len(docs)
            )

            for doc, meta, dist in zip(docs, metas, dists):
                if not meta:
                    continue

                # 1. Enforce cross-tenant retrieval isolation validation
                retrieved_org = meta.get("organization_id")
                retrieved_ws = meta.get("workspace_id")
                if retrieved_org != str(organization_id) or retrieved_ws != str(
                    workspace_id
                ):
                    raise TenantIsolationViolationError(
                        f"Tenancy violation: Document retrieved belongs to org={retrieved_org}, ws={retrieved_ws} "
                        f"but search was initiated for org={organization_id}, ws={workspace_id}."
                    )

                # 2. Enforce embedding model and version refresh validation
                meta_model = meta.get("embedding_model")
                meta_version = meta.get("embedding_version")
                if (
                    meta_model != settings.EMBEDDING_MODEL
                    or meta_version != settings.EMBEDDING_VERSION
                ):
                    raise EmbeddingModelMismatchError(
                        f"Stored embedding model '{meta_model}' (version '{meta_version}') does not match "
                        f"currently configured model '{settings.EMBEDDING_MODEL}' (version '{settings.EMBEDDING_VERSION}'). "
                        "Please re-index the dataset."
                    )

                # 3. Calculate Cosine similarity from L2 distance (ChromaDB uses L2 distance by default)
                # similarity = 1.0 / (1.0 + distance)
                similarity = 1.0 / (1.0 + dist)
                if score_threshold is not None and similarity < score_threshold:
                    continue

                formatted_results.append(
                    {"content": doc, "metadata": meta, "score": similarity}
                )

        return formatted_results

    def delete(self, dataset_id: uuid.UUID) -> None:
        """
        Removes all document vectors linked to the given dataset_id.
        """
        self.collection.delete(where={"dataset_id": str(dataset_id)})
        logger.info(f"Purged all vector store documents for dataset {dataset_id}.")

    def statistics(self) -> Dict[str, Any]:
        """
        Returns stats about Chroma collection size.
        """
        try:
            count = self.collection.count()
            return {
                "provider": "chroma",
                "indexed_documents": count,
                "collection_name": self.collection.name,
            }
        except Exception as e:
            logger.error(f"Failed to fetch Chroma stats: {str(e)}")
            return {"provider": "chroma", "error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """
        Checks connection status to Chroma DB.
        """
        try:
            # Try a simple collection count as a heartbeat check
            self.collection.count()
            return {
                "provider": "chroma",
                "healthy": True,
                "diagnostics": {"collection_count": self.collection.count()},
            }
        except Exception as e:
            return {
                "provider": "chroma",
                "healthy": False,
                "diagnostics": {"error": str(e)},
            }
