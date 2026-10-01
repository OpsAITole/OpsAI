"""Structured AI analysis schemas — validated strictly with Pydantic."""

from pydantic import BaseModel, Field, field_validator


class AnalysisClassification(BaseModel):
    category: str = Field(min_length=1, max_length=64)
    severity: str = Field(min_length=1, max_length=32)
    priority: str = Field(min_length=1, max_length=32)


class IncidentAnalysisResult(BaseModel):
    """Canonical structured diagnosis returned by AI providers."""

    summary: str = Field(min_length=1, max_length=4000)
    classification: AnalysisClassification
    symptoms: list[str] = Field(default_factory=list)
    possible_causes: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    recommended_steps: list[str] = Field(default_factory=list)
    similar_incidents: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    next_best_action: str = Field(min_length=1, max_length=2000)
    warnings: list[str] = Field(default_factory=list)

    @field_validator(
        "symptoms",
        "possible_causes",
        "evidence",
        "recommended_steps",
        "similar_incidents",
        "warnings",
        mode="before",
    )
    @classmethod
    def _coerce_none_to_list(cls, value: object) -> object:
        return [] if value is None else value

    @field_validator(
        "symptoms",
        "possible_causes",
        "evidence",
        "recommended_steps",
        "similar_incidents",
        "warnings",
    )
    @classmethod
    def _strip_items(cls, value: list[str]) -> list[str]:
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
