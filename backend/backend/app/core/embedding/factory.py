"""
app/core/embedding/factory.py
-----------------------------
Registry factory returning EmbeddingProvider instances based on application settings.
"""

from app.core.config import settings
from app.core.embedding.provider import EmbeddingProvider
from app.core.embedding.providers.sentence_transformer import (
    SentenceTransformerProvider,
)


class EmbeddingFactory:
    """
    Factory class to instantiate EmbeddingProviders dynamically.
    """

    @staticmethod
    def get_provider() -> EmbeddingProvider:
        provider_name = settings.EMBEDDING_PROVIDER.lower()
        if provider_name == "sentence-transformers":
            return SentenceTransformerProvider(model_name=settings.EMBEDDING_MODEL)
        elif provider_name == "ollama":
            from app.core.embedding.providers.ollama import OllamaEmbeddingProvider

            return OllamaEmbeddingProvider(model_name=settings.EMBEDDING_MODEL)
        elif provider_name == "openai":
            from app.core.embedding.providers.openai import OpenAIEmbeddingProvider

            return OpenAIEmbeddingProvider(model_name=settings.EMBEDDING_MODEL)
        else:
            raise ValueError(f"Unsupported Embedding provider: {provider_name}")
