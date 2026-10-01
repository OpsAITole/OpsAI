from fastapi import APIRouter

from app.schemas import StatusResponse
from app.services import StatusService

router = APIRouter()


@router.get("/status", response_model=StatusResponse)
def get_status() -> StatusResponse:
    """Product status for the frontend health indicator."""
    return StatusService.get_status()
