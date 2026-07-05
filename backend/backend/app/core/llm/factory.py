from app.core.config import settings
from app.core.llm.provider import LLMProvider
from app.core.llm.providers.ollama import OllamaProvider


class LLMFactory:
    """
    Registry factory returning LLMProvider instances based on config.

    Why this file changed: Provide central LLM provider resolution.
    What changed: Added LLMFactory static class with Gemini routing.
    Dependencies: settings, LLMProvider, OllamaProvider, GeminiProvider.
    Risks: Unsupported configuration keys.
    Rollback procedure: Revert factory.py to Ollama-only version.
    """

    @staticmethod
    def get_provider() -> LLMProvider:
        provider_name = settings.LLM_PROVIDER.lower()
        if provider_name == "ollama":
            return OllamaProvider()
        elif provider_name == "gemini":
            # Lazy import to avoid loading google-genai SDK when unused
            from app.core.llm.providers.gemini import GeminiProvider

            return GeminiProvider()
        else:
            raise ValueError(f"Unsupported LLM provider: {provider_name}")
