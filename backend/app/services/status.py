"""Status service — Phase 1."""

from app.core.config import settings
from app.schemas import StatusResponse


class StatusService:
    @staticmethod
    def get_status() -> StatusResponse:
        return StatusResponse(
            service="OpsAI API",
            status="online",
            version="0.2.0",
            environment=settings.environment,
        )
