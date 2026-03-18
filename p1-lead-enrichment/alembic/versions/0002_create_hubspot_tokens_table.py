"""create hubspot tokens table

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-18
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "hubspot_tokens",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("client_api_key", sa.String(), nullable=False, unique=True),
        sa.Column("access_token", sa.String(), nullable=False),
        sa.Column("refresh_token", sa.String(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_hubspot_tokens_client_api_key", "hubspot_tokens", ["client_api_key"])


def downgrade() -> None:
    op.drop_index("ix_hubspot_tokens_client_api_key", table_name="hubspot_tokens")
    op.drop_table("hubspot_tokens")
