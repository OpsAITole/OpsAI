"""AI provider stubs — no behavior in Phase 1."""

from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    """Interface for future LLM providers (OpenAI, Anthropic, etc.)."""

    @abstractmethod
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Return a model completion. Not implemented in Phase 1."""
        raise NotImplementedError


class NoOpAIProvider(AIProvider):
    """Placeholder provider that refuses to invent AI behavior."""

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        raise NotImplementedError("AI providers are not enabled in Phase 1 (Foundation).")


def get_ai_provider() -> AIProvider:
    """Factory — always returns NoOp until Phase 5+."""
    return NoOpAIProvider()
