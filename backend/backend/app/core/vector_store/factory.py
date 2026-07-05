"""
app/core/vector_store/factory.py
--------------------------------
Factory registry returning VectorStore instances based on config.
"""

from app.core.config import settings
from app.core.vector_store.provider import VectorStore
from app.core.vector_store.providers.chroma import ChromaVectorStore


class VectorStoreFactory:
    """
    Factory class to instantiate VectorStores dynamically.
    """

    @staticmethod
    def get_vector_store() -> VectorStore:
        provider_name = settings.VECTOR_PROVIDER.lower()
        if provider_name == "chroma":
            return ChromaVectorStore(
                collection_name=settings.VECTOR_COLLECTION_NAME,
                db_dir=settings.VECTOR_DB_DIR,
            )
        elif provider_name == "pgvector":
            from app.core.vector_store.providers.pgvector import PgVectorStore

            return PgVectorStore(collection_name=settings.VECTOR_COLLECTION_NAME)
        else:
            raise ValueError(f"Unsupported Vector Store provider: {provider_name}")
