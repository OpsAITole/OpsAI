"""Incident data-access helpers."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import (
    Incident,
    IncidentCategory,
    IncidentPriority,
    IncidentSeverity,
    IncidentStatus,
)


def _parse_ticket_seq(ticket_number: str) -> int:
    try:
        return int(ticket_number.split("-", 1)[1])
    except (IndexError, ValueError):
        return 0


def next_ticket_number(db: Session) -> str:
    """Generate INC-0001 style ticket numbers from the current max sequence."""
    rows = db.scalars(select(Incident.ticket_number)).all()
    next_seq = max((_parse_ticket_seq(t) for t in rows), default=0) + 1
    return f"INC-{next_seq:04d}"


def create_incident(
    db: Session,
    *,
    ticket_number: str,
    title: str,
    description: str,
    status: IncidentStatus,
    priority: IncidentPriority,
    severity: IncidentSeverity,
    category: IncidentCategory,
    affected_service: str | None,
    affected_system: str | None,
    created_by_id: UUID,
) -> Incident:
    incident = Incident(
        ticket_number=ticket_number,
        title=title,
        description=description,
        status=status,
        priority=priority,
        severity=severity,
        category=category,
        affected_service=affected_service,
        affected_system=affected_system,
        created_by_id=created_by_id,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def get_by_id(db: Session, incident_id: UUID) -> Incident | None:
    return db.get(Incident, incident_id)


def delete_incident(db: Session, incident: Incident) -> None:
    db.delete(incident)
    db.commit()


def save(db: Session, incident: Incident) -> Incident:
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def list_incidents(
    db: Session,
    *,
    search: str | None = None,
    status: IncidentStatus | None = None,
    priority: IncidentPriority | None = None,
    category: IncidentCategory | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    offset: int = 0,
    limit: int = 50,
) -> tuple[list[Incident], int]:
    filters: list = []
    if search:
        like = f"%{search.strip()}%"
        filters.append(
            (Incident.title.ilike(like))
            | (Incident.description.ilike(like))
            | (Incident.ticket_number.ilike(like))
            | (Incident.affected_service.ilike(like))
            | (Incident.affected_system.ilike(like))
        )
    if status is not None:
        filters.append(Incident.status == status)
    if priority is not None:
        filters.append(Incident.priority == priority)
    if category is not None:
        filters.append(Incident.category == category)
    if created_from is not None:
        filters.append(Incident.created_at >= created_from)
    if created_to is not None:
        filters.append(Incident.created_at <= created_to)

    sort_map = {
        "created_at": Incident.created_at,
        "updated_at": Incident.updated_at,
        "priority": Incident.priority,
        "status": Incident.status,
        "title": Incident.title,
        "ticket_number": Incident.ticket_number,
    }
    sort_col = sort_map.get(sort_by, Incident.created_at)
    order = sort_col.asc() if sort_dir.lower() == "asc" else sort_col.desc()

    count_stmt = select(func.count()).select_from(Incident)
    list_stmt: Select[tuple[Incident]] = select(Incident)
    if filters:
        count_stmt = count_stmt.where(*filters)
        list_stmt = list_stmt.where(*filters)

    total = int(db.scalar(count_stmt) or 0)
    items = list(db.scalars(list_stmt.order_by(order).offset(offset).limit(limit)).all())
    return items, total
