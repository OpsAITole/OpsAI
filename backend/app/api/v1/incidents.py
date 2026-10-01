"""Incident route stubs — future contracts (Phase 3+)."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from app.schemas import IncidentCreate, IncidentRead

router = APIRouter()


@router.get("", response_model=list[IncidentRead], status_code=status.HTTP_501_NOT_IMPLEMENTED)
def list_incidents() -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Incidents API not implemented in Phase 1"
    )


@router.post("", response_model=IncidentRead, status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create_incident(_payload: IncidentCreate) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Incidents API not implemented in Phase 1"
    )


@router.get("/{incident_id}", response_model=IncidentRead, status_code=status.HTTP_501_NOT_IMPLEMENTED)
def get_incident(_incident_id: UUID) -> None:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Incidents API not implemented in Phase 1"
    )
