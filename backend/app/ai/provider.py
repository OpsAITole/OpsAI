"""AIProvider protocol — swap implementations via AI_PROVIDER env."""

from abc import ABC, abstractmethod
from typing import Any

from app.ai.schemas import IncidentAnalysisResult


class AIProvider(ABC):
    """Decoupled LLM interface. Assistance-only — never executes production changes."""

    name: str = "base"

    @abstractmethod
    def analyze_incident(self, prompt: str, **kwargs: Any) -> IncidentAnalysisResult:
        """Return a structured incident analysis for the given prompt."""

    def generate_summary(self, prompt: str, **kwargs: Any) -> str:
        """Thin stub — summary generation not wired in UI yet."""
        result = self.analyze_incident(prompt, **kwargs)
        return result.summary

    def generate_troubleshooting_steps(self, prompt: str, **kwargs: Any) -> list[str]:
        """Thin stub — steps generation not wired in UI yet."""
        result = self.analyze_incident(prompt, **kwargs)
        return result.recommended_steps

    def generate_report(self, prompt: str, **kwargs: Any) -> str:
        """Thin stub — report generation not wired in UI yet."""
        result = self.analyze_incident(prompt, **kwargs)
        lines = [
            result.summary,
            "",
            f"Próxima mejor acción: {result.next_best_action}",
            f"Confianza: {result.confidence:.0%}",
        ]
        if result.recommended_steps:
            lines.append("")
            lines.append("Pasos recomendados:")
            lines.extend(f"- {step}" for step in result.recommended_steps)
        return "\n".join(lines)
