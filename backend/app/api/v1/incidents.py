"""Incident route stubs — protected; full CRUD in Phase 3+."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.core.security import CurrentUser
from app.schemas import IncidentCreate, IncidentRead

router = APIRouter()


@router.get("", response_model=list[IncidentRead], status_code=status.HTTP_501_NOT_IMPLEMENTED)
def list_incidents(_user: CurrentUser) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Incidents API not implemented yet"
    )


@router.post("", response_model=IncidentRead, status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create_incident(_payload: IncidentCreate, _user: CurrentUser) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Incidents API not implemented yet"
    )


@router.get("/{incident_id}", response_model=IncidentRead, status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_incident(_incident_id: UUID, _user: CurrentUser) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Incidents API not implemented yet"
    )
