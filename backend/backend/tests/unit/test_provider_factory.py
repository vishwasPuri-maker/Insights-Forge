import pytest
from app.core.config import settings
from app.core.llm.factory import LLMFactory


def test_unsupported_provider():
    """
    Verifies that LLMFactory throws a ValueError when configured with an unsupported provider.
    """
    orig_provider = settings.LLM_PROVIDER
    try:
        settings.LLM_PROVIDER = "unsupported_provider_xyz"
        with pytest.raises(ValueError) as exc_info:
            LLMFactory.get_provider()
        assert "Unsupported LLM provider" in str(exc_info.value)
    finally:
        settings.LLM_PROVIDER = orig_provider
