"""add support audit tables

Revision ID: 20260417_0005
Revises: 20260417_0004
Create Date: 2026-04-17 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260417_0005"
down_revision = "20260417_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("actor_user_id", sa.String(), nullable=True),
        sa.Column("actor_role", sa.String(), nullable=True),
        sa.Column("action", sa.String(length=128), nullable=False),
        sa.Column("target_type", sa.String(length=64), nullable=True),
        sa.Column("target_id", sa.String(length=128), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_actor_user_id", "audit_logs", ["actor_user_id"])
    op.create_index("ix_audit_logs_actor_role", "audit_logs", ["actor_role"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_target_type", "audit_logs", ["target_type"])
    op.create_index("ix_audit_logs_target_id", "audit_logs", ["target_id"])

    op.create_table(
        "ai_rate_limit_events",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("allowed", sa.Boolean(), nullable=False),
        sa.Column("remaining", sa.Integer(), nullable=False),
        sa.Column("retry_after_seconds", sa.Integer(), nullable=False),
        sa.Column("rule_max_requests", sa.Integer(), nullable=False),
        sa.Column("rule_window_seconds", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.String(), nullable=True),
        sa.Column("institution_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_rate_limit_events_key", "ai_rate_limit_events", ["key"])
    op.create_index("ix_ai_rate_limit_events_allowed", "ai_rate_limit_events", ["allowed"])
    op.create_index("ix_ai_rate_limit_events_actor_user_id", "ai_rate_limit_events", ["actor_user_id"])
    op.create_index("ix_ai_rate_limit_events_institution_id", "ai_rate_limit_events", ["institution_id"])

    # Best-effort Postgres enum update for UserRole (noop on SQLite).
    try:
        op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'technical_support'")
    except Exception:
        pass


def downgrade() -> None:
    op.drop_index("ix_ai_rate_limit_events_institution_id", table_name="ai_rate_limit_events")
    op.drop_index("ix_ai_rate_limit_events_actor_user_id", table_name="ai_rate_limit_events")
    op.drop_index("ix_ai_rate_limit_events_allowed", table_name="ai_rate_limit_events")
    op.drop_index("ix_ai_rate_limit_events_key", table_name="ai_rate_limit_events")
    op.drop_table("ai_rate_limit_events")

    op.drop_index("ix_audit_logs_target_id", table_name="audit_logs")
    op.drop_index("ix_audit_logs_target_type", table_name="audit_logs")
    op.drop_index("ix_audit_logs_action", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_role", table_name="audit_logs")
    op.drop_index("ix_audit_logs_actor_user_id", table_name="audit_logs")
    op.drop_table("audit_logs")

