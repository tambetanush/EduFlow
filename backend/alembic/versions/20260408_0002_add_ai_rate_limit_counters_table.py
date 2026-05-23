"""add ai_rate_limit_counters table

Revision ID: 20260408_0002
Revises: 20260408_0001
Create Date: 2026-04-08 13:15:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260408_0002"
down_revision = "20260408_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_rate_limit_counters",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("request_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key", "window_start", name="uq_ai_rate_limit_counter_key_window"),
    )
    op.create_index("ix_ai_rate_limit_counters_key", "ai_rate_limit_counters", ["key"])
    op.create_index("ix_ai_rate_limit_counters_window_start", "ai_rate_limit_counters", ["window_start"])


def downgrade() -> None:
    op.drop_index("ix_ai_rate_limit_counters_window_start", table_name="ai_rate_limit_counters")
    op.drop_index("ix_ai_rate_limit_counters_key", table_name="ai_rate_limit_counters")
    op.drop_table("ai_rate_limit_counters")
