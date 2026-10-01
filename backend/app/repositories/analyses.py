"""Incident analysis persistence helpers."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import IncidentAnalysis


def create_analysis(
    db: Session,
    *,
    incident_id: UUID,
    provider: str,
    summary: str,
    confidence: float,
    next_best_action: str,
    result_json: dict,
    created_by_id: UUID | None,
) -> IncidentAnalysis:
    row = IncidentAnalysis(
        incident_id=incident_id,
        provider=provider,
        summary=summary,
        confidence=confidence,
        next_best_action=next_best_action,
        result_json=result_json,
        created_by_id=created_by_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_latest_for_incident(db: Session, incident_id: UUID) -> IncidentAnalysis | None:
    stmt = (
        select(IncidentAnalysis)
        .where(IncidentAnalysis.incident_id == incident_id)
        .order_by(IncidentAnalysis.created_at.desc())
        .limit(1)
    )
    return db.scalars(stmt).first()


def list_for_incident(db: Session, incident_id: UUID) -> list[IncidentAnalysis]:
    stmt = (
        select(IncidentAnalysis)
        .where(IncidentAnalysis.incident_id == incident_id)
        .order_by(IncidentAnalysis.created_at.asc())
    )
    return list(db.scalars(stmt).all())
