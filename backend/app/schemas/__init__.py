"""Pydantic schemas for OpsAI API contracts."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models import (
    IncidentCategory,
    IncidentPriority,
    IncidentSeverity,
    IncidentStatus,
    UserRole,
)


class StatusResponse(BaseModel):
    service: str = "OpsAI API"
    status: str = "online"
    version: str = "0.3.0"
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


# --- Incidents (Phase 3) ---


class IncidentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str = ""
    category: IncidentCategory = IncidentCategory.OTHER
    priority: IncidentPriority = IncidentPriority.MEDIUM
    severity: IncidentSeverity | None = None
    affected_service: str | None = Field(default=None, max_length=255)
    affected_system: str | None = Field(default=None, max_length=255)


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    status: IncidentStatus | None = None
    priority: IncidentPriority | None = None
    severity: IncidentSeverity | None = None
    category: IncidentCategory | None = None
    affected_service: str | None = Field(default=None, max_length=255)
    affected_system: str | None = Field(default=None, max_length=255)


class IncidentRead(BaseModel):
    id: UUID
    ticket_number: str
    title: str
    description: str
    status: IncidentStatus
    priority: IncidentPriority
    severity: IncidentSeverity
    category: IncidentCategory
    affected_service: str | None
    affected_system: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None

    model_config = {"from_attributes": True}


class IncidentListResponse(BaseModel):
    items: list[IncidentRead]
    total: int


class IncidentTimelineEvent(BaseModel):
    id: str
    type: str
    message: str
    at: datetime


class IncidentDetail(IncidentRead):
    timeline: list[IncidentTimelineEvent] = []
