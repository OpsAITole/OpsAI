"""Phase 3 — reshape incidents table to the OpsAI incident contract."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_phase3_incidents"
down_revision: Union[str, None] = "0001_phase2_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Incidents were never written in Phase 1/2 (API returned 501) — recreate cleanly.
    op.drop_table("incidents")
    op.create_table(
        "incidents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("ticket_number", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("priority", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("affected_service", sa.String(length=255), nullable=True),
        sa.Column("affected_system", sa.String(length=255), nullable=True),
        sa.Column("created_by_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_incidents_ticket_number"), "incidents", ["ticket_number"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_incidents_ticket_number"), table_name="incidents")
    op.drop_table("incidents")
    op.create_table(
        "incidents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column("created_by_id", sa.UUID(), nullable=True),
        sa.Column("assigned_to_id", sa.UUID(), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["assigned_to_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
