"""SQLAlchemy models for OpsAI."""

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base

# JSONB on Postgres; plain JSON elsewhere (e.g. SQLite unit tests)
JSONType = JSON().with_variant(JSONB(), "postgresql")


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    TECHNICIAN = "TECHNICIAN"
    VIEWER = "VIEWER"


class IncidentStatus(str, enum.Enum):
    NEW = "NEW"
    INVESTIGATING = "INVESTIGATING"
    WAITING = "WAITING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class IncidentPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentCategory(str, enum.Enum):
    NETWORK = "NETWORK"
    WINDOWS = "WINDOWS"
    LINUX = "LINUX"
    DATABASE = "DATABASE"
    APPLICATION = "APPLICATION"
    SECURITY = "SECURITY"
    VPN = "VPN"
    DNS = "DNS"
    CLOUD = "CLOUD"
    HARDWARE = "HARDWARE"
    OTHER = "OTHER"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=False, length=32),
        default=UserRole.VIEWER,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    created_incidents: Mapped[list["Incident"]] = relationship(
        "Incident", back_populates="creator", foreign_keys="Incident.created_by_id"
    )
    analyses: Mapped[list["IncidentAnalysis"]] = relationship(
        "IncidentAnalysis", back_populates="creator", foreign_keys="IncidentAnalysis.created_by_id"
    )


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_number: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, name="incident_status", native_enum=False, length=32),
        default=IncidentStatus.NEW,
        nullable=False,
    )
    priority: Mapped[IncidentPriority] = mapped_column(
        Enum(IncidentPriority, name="incident_priority", native_enum=False, length=32),
        default=IncidentPriority.MEDIUM,
        nullable=False,
    )
    severity: Mapped[IncidentSeverity] = mapped_column(
        Enum(IncidentSeverity, name="incident_severity", native_enum=False, length=32),
        default=IncidentSeverity.MEDIUM,
        nullable=False,
    )
    category: Mapped[IncidentCategory] = mapped_column(
        Enum(IncidentCategory, name="incident_category", native_enum=False, length=32),
        default=IncidentCategory.OTHER,
        nullable=False,
    )
    affected_service: Mapped[str | None] = mapped_column(String(255), nullable=True)
    affected_system: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    creator: Mapped[User] = relationship(
        "User", back_populates="created_incidents", foreign_keys=[created_by_id]
    )
    analyses: Mapped[list["IncidentAnalysis"]] = relationship(
        "IncidentAnalysis",
        back_populates="incident",
        cascade="all, delete-orphan",
        order_by="IncidentAnalysis.created_at",
    )


class IncidentAnalysis(Base):
    """Persisted AI diagnosis linked to an incident (assistance-only)."""

    __tablename__ = "incident_analyses"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), index=True, nullable=False
    )
    provider: Mapped[str] = mapped_column(String(64), nullable=False, default="mock")
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    next_best_action: Mapped[str] = mapped_column(Text, nullable=False, default="")
    result_json: Mapped[dict[str, Any]] = mapped_column(JSONType, nullable=False)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    incident: Mapped[Incident] = relationship("Incident", back_populates="analyses")
    creator: Mapped[User | None] = relationship(
        "User", back_populates="analyses", foreign_keys=[created_by_id]
    )
