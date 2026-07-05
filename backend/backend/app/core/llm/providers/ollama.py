"""
Ollama Provider
---------------
Invokes local inference engine APIs for completions and streams with robust timeouts and retries.
"""

import time
import json
import logging
from typing import Any, Dict, List, Generator
import httpx

from app.core.config import settings
from app.core.llm.provider import (
    LLMProvider,
    LLMResponse,
    LLMChunk,
    LLMHealthCheckResponse,
)
from app.core.llm.token_counter import TokenCounter
from app.core.llm.retry import RetryExecutor

logger = logging.getLogger("ollama-provider")


class OllamaProvider(LLMProvider):
    """
    Ollama implementation of LLMProvider for local inference APIs.
    """

    def __init__(self) -> None:
        self.base_url = settings.LLM_BASE_URL.rstrip("/")
        self.model = settings.LLM_MODEL

    def generate(self, messages: List[Dict[str, str]], **kwargs: Any) -> LLMResponse:
        """
        Submits dialog history to the LLM and returns a structured LLMResponse.
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", settings.LLM_TEMPERATURE),
                "num_predict": kwargs.get("max_tokens", settings.LLM_MAX_TOKENS),
            },
        }

        prompt_text = "".join([m.get("content", "") for m in messages])
        prompt_tokens = TokenCounter.estimate_tokens(prompt_text)

        def perform_request():
            with httpx.Client(
                timeout=httpx.Timeout(
                    settings.LLM_TIMEOUT,
                    connect=settings.LLM_TIMEOUT_CONNECT,
                    read=settings.LLM_TIMEOUT_READ,
                    write=settings.LLM_TIMEOUT_WRITE,
                )
            ) as client:
                resp = client.post(url, json=payload)
                if resp.status_code != 200:
                    raise httpx.HTTPStatusError(
                        f"HTTP {resp.status_code}", request=resp.request, response=resp
                    )
                return resp.json()

        start_time = time.time()
        try:
            data, retry_count = RetryExecutor.execute(perform_request)
            latency_ms = int((time.time() - start_time) * 1000)

            content = data["message"]["content"]
            completion_tokens = TokenCounter.estimate_tokens(content)

            logger.info(
                "Ollama request successful",
                extra={
                    "provider": "ollama",
                    "model": self.model,
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                    "latency_ms": latency_ms,
                    "retry_count": retry_count,
                },
            )

            return LLMResponse(
                status="success",
                content=content,
                model=self.model,
                provider="ollama",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
                latency_ms=latency_ms,
                retry_count=retry_count,
            )
        except Exception as e:
            logger.error(f"Ollama request failed after retries: {str(e)}")
            return LLMResponse(
                status="error",
                content="The AI inference engine is currently unavailable. Please try again shortly.",
                error_details=str(e),
                model=self.model,
                provider="ollama",
                retry_count=settings.LLM_MAX_RETRIES,
            )

    def stream(
        self, messages: List[Dict[str, str]], **kwargs: Any
    ) -> Generator[LLMChunk, None, None]:
        """
        Submits dialog history to the LLM and yields a stream of LLMChunk blocks.
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": kwargs.get("temperature", settings.LLM_TEMPERATURE),
                "num_predict": kwargs.get("max_tokens", settings.LLM_MAX_TOKENS),
            },
        }

        # Define connection establishment closure for retry executor
        def get_stream_response():
            client = httpx.Client(
                timeout=httpx.Timeout(
                    settings.LLM_TIMEOUT,
                    connect=settings.LLM_TIMEOUT_CONNECT,
                    read=settings.LLM_TIMEOUT_READ,
                    write=settings.LLM_TIMEOUT_WRITE,
                )
            )
            req = client.build_request("POST", url, json=payload)
            resp = client.send(req, stream=True)
            if resp.status_code != 200:
                resp.close()
                raise httpx.HTTPStatusError(
                    f"HTTP {resp.status_code}", request=req, response=resp
                )
            return resp, client

        start_time = time.time()

        try:
            (response, client), retry_count = RetryExecutor.execute(get_stream_response)
        except Exception as e:
            logger.error(f"Failed to start Ollama stream after retries: {str(e)}")
            yield LLMChunk(
                text="The AI inference engine is currently unavailable. Please try again shortly.",
                finished=True,
                finish_reason="error",
                model=self.model,
                provider="ollama",
                retry_count=settings.LLM_MAX_RETRIES,
            )
            return

        try:
            with response as r:
                for line in r.iter_lines():
                    if not line:
                        continue
                    try:
                        chunk_data = json.loads(line)
                        text_fragment = chunk_data.get("message", {}).get("content", "")
                        done = chunk_data.get("done", False)

                        latency_ms = int((time.time() - start_time) * 1000)

                        yield LLMChunk(
                            text=text_fragment,
                            finished=done,
                            finish_reason="stop" if done else None,
                            model=self.model,
                            provider="ollama",
                            retry_count=retry_count,
                            latency_ms=latency_ms,
                        )
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse streaming JSON chunk: {line}")
        except Exception as e:
            logger.error(f"Error during streaming token collection: {str(e)}")
            yield LLMChunk(
                text="\n[Inference stream interrupted]",
                finished=True,
                finish_reason="error",
                model=self.model,
                provider="ollama",
                retry_count=retry_count,
            )
        finally:
            client.close()

    def health_check(self) -> LLMHealthCheckResponse:
        """
        Checks connectivity to the Ollama tags endpoint and retrieves load state metadata.
        """
        url_tags = f"{self.base_url}/api/tags"
        url_version = f"{self.base_url}/api/version"

        start_time = time.time()
        try:
            with httpx.Client(timeout=2.0) as client:
                response_tags = client.get(url_tags)
                latency_ms = int((time.time() - start_time) * 1000)

                if response_tags.status_code == 200:
                    models = [m["name"] for m in response_tags.json().get("models", [])]
                    model_found = False
                    for m in models:
                        if self.model in m or m in self.model:
                            model_found = True
                            break

                    version_str = "unknown"
                    try:
                        response_ver = client.get(url_version, timeout=1.0)
                        if response_ver.status_code == 200:
                            version_str = response_ver.json().get("version", "unknown")
                    except Exception:
                        pass

                    return LLMHealthCheckResponse(
                        reachable=True,
                        model=self.model,
                        version=version_str,
                        provider="ollama",
                        status="healthy" if model_found else "degraded",
                        loaded=model_found,
                        streaming=settings.LLM_STREAMING_ENABLED,
                        latency_ms=latency_ms,
                    )
        except Exception as e:
            logger.warning(f"Ollama health check failed: {str(e)}")

        return LLMHealthCheckResponse(
            reachable=False,
            model=self.model,
            version=None,
            provider="ollama",
            status="unhealthy",
            loaded=False,
            streaming=settings.LLM_STREAMING_ENABLED,
            latency_ms=None,
        )
