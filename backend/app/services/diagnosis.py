"""DiagnosisService — independent AI analysis orchestration (not a fat endpoint)."""

from __future__ import annotations

import re
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.ai import AIProviderError, IncidentAnalysisResult, get_ai_provider
from app.models import Incident, IncidentAnalysis, User
from app.repositories import analyses as analyses_repo
from app.repositories import incidents as incidents_repo
from app.schemas import IncidentAnalysisRead
from app.services import incidents as incidents_service

_PROMPTS_DIR = Path(__file__).resolve().parent.parent / "ai" / "prompts"
_STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "that",
    "this",
    "have",
    "has",
    "are",
    "was",
    "were",
    "been",
    "being",
    "into",
    "about",
    "over",
    "under",
    "cannot",
    "users",
    "user",
    "issue",
    "error",
    "failed",
    "failure",
}


def _load_prompt_template() -> str:
    path = _PROMPTS_DIR / "incident_analysis.txt"
    return path.read_text(encoding="utf-8")


def _keywords(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]{3,}", text.lower())
    return {t for t in tokens if t not in _STOPWORDS}


def _format_incident_context(incident: Incident) -> str:
    return "\n".join(
        [
            f"Ticket: {incident.ticket_number}",
            f"Title: {incident.title}",
            f"Description: {incident.description or '(empty)'}",
            f"Status: {incident.status.value}",
            f"Category: {incident.category.value}",
            f"Priority: {incident.priority.value}",
            f"Severity: {incident.severity.value}",
            f"Affected service: {incident.affected_service or '(none)'}",
            f"Affected system: {incident.affected_system or '(none)'}",
        ]
    )


def find_similar_incidents(db: Session, incident: Incident, *, limit: int = 5) -> list[Incident]:
    """
    Phase-3-style similarity: same category, overlapping service, shared keywords.
    Not pgvector — deferred to a later RAG phase.
    """
    items, _ = incidents_repo.list_incidents(
        db,
        category=incident.category,
        offset=0,
        limit=50,
        sort_by="created_at",
        sort_dir="desc",
    )
    source_keywords = _keywords(f"{incident.title} {incident.description}")
    scored: list[tuple[int, Incident]] = []
    for other in items:
        if other.id == incident.id:
            continue
        score = 0
        if other.category == incident.category:
            score += 3
        if (
            incident.affected_service
            and other.affected_service
            and incident.affected_service.strip().lower() == other.affected_service.strip().lower()
        ):
            score += 4
        if (
            incident.affected_system
            and other.affected_system
            and incident.affected_system.strip().lower() == other.affected_system.strip().lower()
        ):
            score += 2
        overlap = source_keywords & _keywords(f"{other.title} {other.description}")
        score += min(len(overlap), 5)
        if score > 0:
            scored.append((score, other))
    scored.sort(key=lambda pair: (-pair[0], pair[1].created_at))
    return [inc for _, inc in scored[:limit]]


def _format_similar(similar: list[Incident]) -> str:
    if not similar:
        return "None provided."
    lines = []
    for inc in similar:
        lines.append(
            f"- {inc.ticket_number}: {inc.title} "
            f"[category={inc.category.value}, status={inc.status.value}, "
            f"service={inc.affected_service or 'n/a'}]"
        )
    return "\n".join(lines)


def build_analysis_prompt(incident: Incident, similar: list[Incident]) -> str:
    template = _load_prompt_template()
    return (
        template.replace("{{incident_context}}", _format_incident_context(incident)).replace(
            "{{similar_incidents}}", _format_similar(similar)
        )
    )


def to_read(row: IncidentAnalysis) -> IncidentAnalysisRead:
    result = IncidentAnalysisResult.model_validate(row.result_json)
    return IncidentAnalysisRead(
        id=row.id,
        incident_id=row.incident_id,
        provider=row.provider,
        created_at=row.created_at,
        created_by=row.created_by_id,
        analysis=result,
    )


def get_latest_analysis(db: Session, incident_id: UUID) -> IncidentAnalysisRead:
    incidents_service.get_incident(db, incident_id)
    row = analyses_repo.get_latest_for_incident(db, incident_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No analysis saved for this incident yet",
        )
    return to_read(row)


def analyze_incident(db: Session, incident_id: UUID, user: User) -> IncidentAnalysisRead:
    """
    Receive incident → gather context & similar incidents → prompt → AIProvider
    → validate with Pydantic → persist → return.
    """
    incident = incidents_service.get_incident(db, incident_id)
    similar = find_similar_incidents(db, incident)
    prompt = build_analysis_prompt(incident, similar)

    try:
        provider = get_ai_provider()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    try:
        result = provider.analyze_incident(prompt)
    except AIProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="AI output failed schema validation",
        ) from exc
    except Exception as exc:  # noqa: BLE001 — map unexpected provider failures to safe client error
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI provider failed to produce a valid analysis",
        ) from exc

    try:
        validated = IncidentAnalysisResult.model_validate(result.model_dump())
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="AI output failed schema validation",
        ) from exc

    # Ensure similar_incidents only references provided tickets when possible
    allowed_tickets = {s.ticket_number for s in similar}
    if allowed_tickets:
        filtered_similar = [
            item
            for item in validated.similar_incidents
            if any(ticket in item for ticket in allowed_tickets)
        ]
        validated = validated.model_copy(update={"similar_incidents": filtered_similar})

    row = analyses_repo.create_analysis(
        db,
        incident_id=incident.id,
        provider=getattr(provider, "name", "unknown"),
        summary=validated.summary,
        confidence=validated.confidence,
        next_best_action=validated.next_best_action,
        result_json=validated.model_dump(),
        created_by_id=user.id,
    )
    return to_read(row)
