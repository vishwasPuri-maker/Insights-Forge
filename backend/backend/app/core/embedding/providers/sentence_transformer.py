"""
app/core/embedding/providers/sentence_transformer.py
----------------------------------------------------
Concrete embedding provider using the SentenceTransformers library to run
lightweight embedding models locally and for free.
"""

import logging
from typing import List
from app.core.embedding.provider import EmbeddingProvider

logger = logging.getLogger("embedding-service")


class SentenceTransformerProvider(EmbeddingProvider):
    """
    SentenceTransformer implementation of EmbeddingProvider.
    """

    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        # Lazily import sentence_transformers to optimize startup time
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading local SentenceTransformer model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self._dimension = self.model.get_sentence_embedding_dimension()
        logger.info(
            f"SentenceTransformer model loaded successfully with dimension {self._dimension}."
        )

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single text query.
        """
        try:
            vector = self.model.encode(text)
            return vector.tolist()  # Convert numpy array to list
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of document strings in batch.
        """
        if not texts:
            return []
        try:
            vectors = self.model.encode(texts)
            return vectors.tolist()  # Convert numpy array list of lists
        except Exception as e:
            logger.error(f"Error generating batch document embeddings: {str(e)}")
            raise e
