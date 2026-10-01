"""AI package — provider factory switched by AI_PROVIDER env."""

from functools import lru_cache

from app.ai.mock import MockAIProvider
from app.ai.openai_provider import AIProviderError, OllamaProvider, OpenAIProvider
from app.ai.provider import AIProvider
from app.ai.schemas import AnalysisClassification, IncidentAnalysisResult
from app.core.config import settings

__all__ = [
    "AIProvider",
    "AIProviderError",
    "AnalysisClassification",
    "IncidentAnalysisResult",
    "MockAIProvider",
    "OllamaProvider",
    "OpenAIProvider",
    "get_ai_provider",
]


@lru_cache
def get_ai_provider() -> AIProvider:
    """
    Factory — select provider via AI_PROVIDER without rewriting app code.
    Supported: mock (default), openai, ollama.
    """
    name = (settings.ai_provider or "mock").strip().lower()
    if name in {"", "none", "mock"}:
        return MockAIProvider()
    if name == "openai":
        return OpenAIProvider()
    if name == "ollama":
        return OllamaProvider()
    raise ValueError(f"Unsupported AI_PROVIDER={settings.ai_provider!r}; use mock|openai|ollama")
