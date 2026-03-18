"""create leads table

Revision ID: 0001
Revises:
Create Date: 2026-03-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leads",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("crm_lead_id", sa.String(), nullable=False, unique=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("company", sa.String(), nullable=True),
        sa.Column("enriched_data", sa.JSON(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("tier", sa.String(), nullable=True),
        sa.Column("reason", sa.String(), nullable=True),
        sa.Column("recommended_action", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    # Index on crm_lead_id for fast duplicate detection
    op.create_index("ix_leads_crm_lead_id", "leads", ["crm_lead_id"])


def downgrade() -> None:
    op.drop_index("ix_leads_crm_lead_id", table_name="leads")
    op.drop_table("leads")
