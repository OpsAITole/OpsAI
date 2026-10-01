"""Incident CRUD routes — Phase 3."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import CurrentUser, require_roles
from app.models import (
    IncidentCategory,
    IncidentPriority,
    IncidentStatus,
    User,
    UserRole,
)
from app.schemas import (
    IncidentCreate,
    IncidentDetail,
    IncidentListResponse,
    IncidentRead,
    IncidentUpdate,
    MessageResponse,
)
from app.services import incidents as incidents_service

router = APIRouter()

WriteUser = Annotated[
    User,
    Depends(require_roles(UserRole.ADMIN, UserRole.TECHNICIAN)),
]


@router.get("", response_model=IncidentListResponse)
def list_incidents(
    _user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    search: str | None = Query(default=None, max_length=200),
    status_filter: IncidentStatus | None = Query(default=None, alias="status"),
    priority: IncidentPriority | None = None,
    category: IncidentCategory | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    sort_by: Literal[
        "created_at", "updated_at", "priority", "status", "title", "ticket_number"
    ] = "created_at",
    sort_dir: Literal["asc", "desc"] = "desc",
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> IncidentListResponse:
    return incidents_service.list_incidents(
        db,
        search=search,
        status_filter=status_filter,
        priority=priority,
        category=category,
        created_from=created_from,
        created_to=created_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
        offset=offset,
        limit=limit,
    )


@router.post("", response_model=IncidentRead, status_code=status.HTTP_201_CREATED)
def create_incident(
    payload: IncidentCreate,
    user: WriteUser,
    db: Annotated[Session, Depends(get_db)],
) -> IncidentRead:
    incident = incidents_service.create_incident(db, payload, user)
    return incidents_service.to_read(incident)


@router.get("/{incident_id}", response_model=IncidentDetail)
def get_incident(
    incident_id: UUID,
    _user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> IncidentDetail:
    incident = incidents_service.get_incident(db, incident_id)
    return incidents_service.to_detail(incident)


@router.put("/{incident_id}", response_model=IncidentRead)
def update_incident(
    incident_id: UUID,
    payload: IncidentUpdate,
    _user: WriteUser,
    db: Annotated[Session, Depends(get_db)],
) -> IncidentRead:
    incident = incidents_service.update_incident(db, incident_id, payload)
    return incidents_service.to_read(incident)


@router.delete("/{incident_id}", response_model=MessageResponse)
def delete_incident(
    incident_id: UUID,
    _user: WriteUser,
    db: Annotated[Session, Depends(get_db)],
) -> MessageResponse:
    incidents_service.delete_incident(db, incident_id)
    return MessageResponse(message="Incident deleted")


@router.post(
    "/{incident_id}/analyze",
    status_code=status.HTTP_501_NOT_IMPLEMENTED,
)
def analyze_incident(incident_id: UUID, _user: CurrentUser) -> None:
    """AI analysis arrives in Phase 4 — stub stays 501."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail=f"AI analysis for incident {incident_id} is not implemented yet (Phase 4)",
    )
