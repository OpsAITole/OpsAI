"""Pydantic schemas — Phase 1 status + future auth/incident contracts."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models import IncidentSeverity, IncidentStatus, UserRole


class StatusResponse(BaseModel):
    service: str = "OpsAI API"
    status: str = "online"
    version: str = "0.1.0"
    environment: str


# --- Future auth contracts (schemas only; endpoints return 501) ---


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str | None
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Future incident contracts ---


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str = ""
    severity: IncidentSeverity = IncidentSeverity.medium
    source: str | None = None


class IncidentRead(BaseModel):
    id: UUID
    title: str
    description: str
    status: IncidentStatus
    severity: IncidentSeverity
    source: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
