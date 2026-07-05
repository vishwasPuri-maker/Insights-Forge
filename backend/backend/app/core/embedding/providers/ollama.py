"""
app/core/embedding/providers/ollama.py
--------------------------------------
Ollama implementation of the EmbeddingProvider interface.
Sends requests to local Ollama endpoints using httpx.
"""

import logging
from typing import List, Optional
import httpx

from app.core.config import settings
from app.core.embedding.provider import EmbeddingProvider

logger = logging.getLogger("ollama-embedding")


class OllamaEmbeddingProvider(EmbeddingProvider):
    """
    Embedding Provider using local Ollama service.
    """

    def __init__(self, model_name: str, base_url: Optional[str] = None) -> None:
        self.model_name = model_name
        self.base_url = base_url or settings.LLM_BASE_URL.rstrip("/")
        self._dimension: Optional[int] = None

        # Dynamically probe the model to discover dimension size at startup
        try:
            test_vector = self.embed_query("test")
            self._dimension = len(test_vector)
            logger.info(
                f"Ollama model '{model_name}' active with dimension {self._dimension}."
            )
        except Exception as e:
            # Default fallback for offline or uninitialized startup environments
            logger.warning(
                f"Failed to probe Ollama dimension for model '{model_name}' at startup: {str(e)}. Defaulting to 384."
            )
            self._dimension = 384

    @property
    def dimension(self) -> int:
        return self._dimension or 384

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        """
        url = f"{self.base_url}/api/embeddings"
        payload = {"model": self.model_name, "prompt": text}
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                embedding = data.get("embedding")
                if not embedding or not isinstance(embedding, list):
                    raise ValueError(
                        f"Unexpected response format from Ollama embeddings: {data}"
                    )
                return [float(x) for x in embedding]
        except Exception as e:
            logger.error(
                f"Ollama embedding query failed for model '{self.model_name}': {str(e)}"
            )
            raise e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for list of texts.
        Attempts batch /api/embed, falls back to sequential /api/embeddings.
        """
        if not texts:
            return []

        # Try Ollama's newer batch /api/embed endpoint
        url_embed = f"{self.base_url}/api/embed"
        payload_embed = {"model": self.model_name, "input": texts}
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url_embed, json=payload_embed)
                if response.status_code == 200:
                    data = response.json()
                    embeddings = data.get("embeddings")
                    if embeddings and isinstance(embeddings, list):
                        return [[float(x) for x in emb] for emb in embeddings]
        except Exception as e:
            logger.debug(
                f"Ollama /api/embed failed, falling back to /api/embeddings: {str(e)}"
            )

        # Fallback: sequential query embeddings
        results = []
        for text in texts:
            results.append(self.embed_query(text))
        return results
