"""
LLM Provider Contracts
----------------------
Defines normalized request/response schemas and interfaces for all supported LLM providers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Generator
from pydantic import BaseModel


class LLMResponse(BaseModel):
    """
    Normalized response structure returned by any LLM provider on standard completions.
    """

    status: str  # "success" or "error"
    content: str
    error_details: Optional[str] = None
    model: str
    provider: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    retry_count: int = 0


class LLMChunk(BaseModel):
    """
    Normalized stream chunk yielded by any LLM provider during streaming completions.
    """

    text: str
    finished: bool = False
    finish_reason: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    retry_count: int = 0
    model: str = ""
    provider: str = ""
    conversation_id: Optional[str] = None


class LLMHealthCheckResponse(BaseModel):
    """
    Normalized diagnostic metadata returned by provider health check lookups.
    """

    reachable: bool
    model: str
    version: Optional[str] = None
    provider: str = ""
    status: str = "unhealthy"
    loaded: bool = False
    streaming: bool = False
    latency_ms: Optional[int] = None


class LLMProvider(ABC):
    """
    Abstract base interface representing a contract for LLM provider adapters.
    """

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> LLMResponse:
        """
        Submits dialog history to the LLM and returns a structured LLMResponse.
        """
        pass

    @abstractmethod
    def stream(
        self, messages: List[Dict[str, str]], **kwargs: Any
    ) -> Generator[LLMChunk, None, None]:
        """
        Submits dialog history to the LLM and yields a stream of LLMChunk blocks.
        """
        pass

    @abstractmethod
    def health_check(self) -> LLMHealthCheckResponse:
        """
        Checks connectivity to the LLM server and returns rich diagnostics.
        """
        pass
