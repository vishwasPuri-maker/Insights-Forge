"""
app/core/embedding/providers/openai.py
--------------------------------------
OpenAI implementation of the EmbeddingProvider interface.
Sends requests to OpenAI API (or any OpenAI-compatible API gateway) using httpx.
"""

import logging
from typing import List
import httpx

from app.core.config import settings
from app.core.embedding.provider import EmbeddingProvider

logger = logging.getLogger("openai-embedding")


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    Embedding Provider for OpenAI-compatible embeddings APIs.
    """

    def __init__(
        self,
        model_name: str,
        api_key: str = "",
        base_url: str = "https://api.openai.com/v1",
    ) -> None:
        self.model_name = model_name
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", "")
        self.base_url = base_url.rstrip("/")

        # Dynamically set dimensions based on standard OpenAI specifications
        if "text-embedding-3-large" in model_name:
            self._dimension = 3072
        elif "text-embedding-3-small" in model_name:
            self._dimension = 1536
        elif "text-embedding-ada-002" in model_name:
            self._dimension = 1536
        else:
            self._dimension = 1536  # Standard default fallback

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query.
        """
        results = self.embed_documents([text])
        if not results:
            raise ValueError("No embeddings returned from OpenAI API.")
        return results[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts in batch.
        """
        if not texts:
            return []

        url = f"{self.base_url}/embeddings"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        payload = {"input": texts, "model": self.model_name}

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()

                # Parse OpenAI response format: {"data": [{"embedding": [...], "index": 0}]}
                embeddings_data = data.get("data", [])
                # Sort by index to maintain original ordering
                sorted_data = sorted(embeddings_data, key=lambda x: x.get("index", 0))

                results = []
                for item in sorted_data:
                    emb = item.get("embedding")
                    if emb and isinstance(emb, list):
                        results.append([float(x) for x in emb])

                if len(results) != len(texts):
                    raise ValueError(
                        f"OpenAI returned {len(results)} embeddings for {len(texts)} input texts."
                    )
                return results
        except Exception as e:
            logger.error(
                f"OpenAI embedding batch request failed for model '{self.model_name}': {str(e)}"
            )
            raise e
