"""Pydantic schemas for OpsAI API contracts."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models import IncidentSeverity, IncidentStatus, UserRole


class StatusResponse(BaseModel):
    service: str = "OpsAI API"
    status: str = "online"
    version: str = "0.2.0"
    environment: str


# --- Auth ---


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=255)
    role: UserRole = UserRole.VIEWER


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    role: UserRole
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class MessageResponse(BaseModel):
    message: str


class OAuthProviderStub(BaseModel):
    provider: str
    status: str = "not_implemented"
    detail: str = "OAuth is stubbed for a later phase"


# --- Incidents (Phase 3 contracts) ---


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
