"""OpenAI chat-completions adapter — used when AI_PROVIDER=openai and a key is set."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx
from pydantic import ValidationError

from app.ai.provider import AIProvider
from app.ai.schemas import IncidentAnalysisResult
from app.core.config import settings


class AIProviderError(Exception):
    """Raised when the provider cannot produce a usable analysis."""

    def __init__(self, message: str, *, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


def _extract_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", cleaned, re.IGNORECASE)
    if fence:
        cleaned = fence.group(1).strip()
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        data = json.loads(cleaned[start : end + 1])
        if isinstance(data, dict):
            return data
    raise AIProviderError("Model returned non-JSON output", status_code=502)


class OpenAIProvider(AIProvider):
    """
    Calls OpenAI Chat Completions and validates the structured analysis.
    Requires AI_API_KEY. Does not invent execution of production actions.
    """

    name = "openai"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.ai_api_key
        self.model = model or settings.ai_model or "gpt-4o-mini"
        self.base_url = (base_url or settings.ai_base_url or "https://api.openai.com/v1").rstrip("/")
        self.timeout = timeout

    def analyze_incident(self, prompt: str, **kwargs: Any) -> IncidentAnalysisResult:
        del kwargs
        if not self.api_key:
            raise AIProviderError(
                "OpenAI provider is selected but AI_API_KEY is not configured",
                status_code=503,
            )

        url = f"{self.base_url}/chat/completions"
        payload = {
            "model": self.model,
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are OpsAI. Return only valid JSON matching the requested schema. "
                        "Assistance only — never claim production actions were executed."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, headers=headers, json=payload)
        except httpx.HTTPError as exc:
            raise AIProviderError(f"OpenAI request failed: {exc}", status_code=502) from exc

        if response.status_code >= 400:
            raise AIProviderError(
                f"OpenAI API error ({response.status_code})",
                status_code=502,
            )

        try:
            body = response.json()
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise AIProviderError("Unexpected OpenAI response shape", status_code=502) from exc

        try:
            data = _extract_json_object(content if isinstance(content, str) else json.dumps(content))
            return IncidentAnalysisResult.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise AIProviderError(
                "AI output failed schema validation",
                status_code=422,
            ) from exc


class OllamaProvider(AIProvider):
    """
    Optional Ollama adapter skeleton (AI_PROVIDER=ollama).
    Uses the OpenAI-compatible /v1/chat/completions endpoint when available.
    """

    name = "ollama"

    def __init__(self) -> None:
        base = settings.ai_base_url or "http://localhost:11434/v1"
        self._delegate = OpenAIProvider(
            api_key=settings.ai_api_key or "ollama",
            model=settings.ai_model or "llama3.2",
            base_url=base,
        )

    def analyze_incident(self, prompt: str, **kwargs: Any) -> IncidentAnalysisResult:
        return self._delegate.analyze_incident(prompt, **kwargs)
