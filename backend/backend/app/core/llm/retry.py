"""
Retry Executor
--------------
Decoupled resilience mechanism executing network calls with configurable backoff and retries.
"""

import time
import logging
from typing import Callable, Any, TypeVar
import httpx
from app.core.config import settings

logger = logging.getLogger("retry-executor")

T = TypeVar("T")


class RetryExecutor:
    """
    Executes calls with exponential backoff retries for resilient API connections.
    """

    @staticmethod
    def execute(
        operation: Callable[..., T], *args: Any, **kwargs: Any
    ) -> tuple[T, int]:
        """
        Executes a callable, retrying on network or timeout exceptions.
        Returns a tuple of (result, retry_count).
        """
        max_retries = settings.LLM_MAX_RETRIES
        backoff_factor = settings.LLM_RETRY_BACKOFF

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                result = operation(*args, **kwargs)
                return result, attempt - 1
            except (httpx.RequestError, httpx.TimeoutException) as e:
                last_error = e
                logger.warning(
                    f"Inference attempt {attempt}/{max_retries} failed with connection error: {str(e)}"
                )
                if attempt == max_retries:
                    break

                # Exponential backoff delay
                sleep_time = backoff_factor * attempt
                time.sleep(sleep_time)

        # If all retries failed, raise the final exception
        raise last_error
