"""Incident business logic."""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import (
    Incident,
    IncidentCategory,
    IncidentPriority,
    IncidentSeverity,
    IncidentStatus,
    User,
)
from app.repositories import analyses as analyses_repo
from app.repositories import incidents as incidents_repo
from app.schemas import (
    IncidentCreate,
    IncidentDetail,
    IncidentListResponse,
    IncidentRead,
    IncidentTimelineEvent,
    IncidentUpdate,
)

_RESOLVED_STATUSES = {IncidentStatus.RESOLVED, IncidentStatus.CLOSED}


def _severity_from_priority(priority: IncidentPriority) -> IncidentSeverity:
    return IncidentSeverity(priority.value)


def to_read(incident: Incident) -> IncidentRead:
    return IncidentRead(
        id=incident.id,
        ticket_number=incident.ticket_number,
        title=incident.title,
        description=incident.description,
        status=incident.status,
        priority=incident.priority,
        severity=incident.severity,
        category=incident.category,
        affected_service=incident.affected_service,
        affected_system=incident.affected_system,
        created_by=incident.created_by_id,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        resolved_at=incident.resolved_at,
    )


def build_timeline(incident: Incident, db: Session | None = None) -> list[IncidentTimelineEvent]:
    """Timeline from create/update/resolved plus saved AI analysis events."""
    events = [
        IncidentTimelineEvent(
            id=f"{incident.id}-created",
            type="created",
            message=f"Incidente {incident.ticket_number} abierto",
            at=incident.created_at,
        )
    ]
    if incident.updated_at and incident.updated_at != incident.created_at:
        events.append(
            IncidentTimelineEvent(
                id=f"{incident.id}-updated",
                type="updated",
                message=f"Estado {incident.status.value} · prioridad {incident.priority.value}",
                at=incident.updated_at,
            )
        )
    if incident.resolved_at is not None:
        events.append(
            IncidentTimelineEvent(
                id=f"{incident.id}-resolved",
                type="resolved",
                message="Incidente marcado como resuelto/cerrado",
                at=incident.resolved_at,
            )
        )

    if db is not None:
        for analysis in analyses_repo.list_for_incident(db, incident.id):
            conf_pct = int(round(analysis.confidence * 100))
            events.append(
                IncidentTimelineEvent(
                    id=str(analysis.id),
                    type="analyzed",
                    message=(
                        f"Análisis IA ({analysis.provider}) guardado — "
                        f"confianza {conf_pct}%. Solo asistencia; no se han ejecutado cambios en producción."
                    ),
                    at=analysis.created_at,
                )
            )

    events.sort(key=lambda e: e.at)
    return events


def to_detail(incident: Incident, db: Session | None = None) -> IncidentDetail:
    # Lazy import avoids circular dependency with diagnosis service.
    from app.services import diagnosis as diagnosis_service

    base = to_read(incident)
    latest = None
    if db is not None:
        row = analyses_repo.get_latest_for_incident(db, incident.id)
        if row is not None:
            latest = diagnosis_service.to_read(row)
    return IncidentDetail(
        **base.model_dump(),
        timeline=build_timeline(incident, db),
        latest_analysis=latest,
    )


def create_incident(db: Session, payload: IncidentCreate, user: User) -> Incident:
    severity = payload.severity or _severity_from_priority(payload.priority)
    ticket = incidents_repo.next_ticket_number(db)
    return incidents_repo.create_incident(
        db,
        ticket_number=ticket,
        title=payload.title.strip(),
        description=payload.description or "",
        status=IncidentStatus.NEW,
        priority=payload.priority,
        severity=severity,
        category=payload.category,
        affected_service=payload.affected_service,
        affected_system=payload.affected_system,
        created_by_id=user.id,
    )


def get_incident(db: Session, incident_id: UUID) -> Incident:
    incident = incidents_repo.get_by_id(db, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incidente no encontrado")
    return incident


def list_incidents(
    db: Session,
    *,
    search: str | None = None,
    status_filter: IncidentStatus | None = None,
    priority: IncidentPriority | None = None,
    category: IncidentCategory | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    offset: int = 0,
    limit: int = 50,
) -> IncidentListResponse:
    items, total = incidents_repo.list_incidents(
        db,
        search=search,
        status=status_filter,
        priority=priority,
        category=category,
        created_from=created_from,
        created_to=created_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
        offset=offset,
        limit=limit,
    )
    return IncidentListResponse(items=[to_read(i) for i in items], total=total)


def update_incident(db: Session, incident_id: UUID, payload: IncidentUpdate) -> Incident:
    incident = get_incident(db, incident_id)
    data = payload.model_dump(exclude_unset=True)

    if "title" in data and data["title"] is not None:
        incident.title = data["title"].strip()
    if "description" in data and data["description"] is not None:
        incident.description = data["description"]
    if "priority" in data and data["priority"] is not None:
        incident.priority = data["priority"]
    if "severity" in data and data["severity"] is not None:
        incident.severity = data["severity"]
    if "category" in data and data["category"] is not None:
        incident.category = data["category"]
    if "affected_service" in data:
        incident.affected_service = data["affected_service"]
    if "affected_system" in data:
        incident.affected_system = data["affected_system"]

    if "status" in data and data["status"] is not None:
        new_status: IncidentStatus = data["status"]
        incident.status = new_status
        if new_status in _RESOLVED_STATUSES and incident.resolved_at is None:
            incident.resolved_at = datetime.now(UTC)
        elif new_status not in _RESOLVED_STATUSES:
            incident.resolved_at = None

    incident.updated_at = datetime.now(UTC)
    return incidents_repo.save(db, incident)


def delete_incident(db: Session, incident_id: UUID) -> None:
    incident = get_incident(db, incident_id)
    incidents_repo.delete_incident(db, incident)
