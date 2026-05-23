"""add scheduled ai report tables

Revision ID: 20260417_0004
Revises: 20260408_0003
Create Date: 2026-04-17 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "20260417_0004"
down_revision = "20260408_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    freq_enum = sa.Enum("DAILY", "WEEKLY", name="scheduledreportfrequency")
    status_enum = sa.Enum("ACTIVE", "PAUSED", name="scheduledreportstatus")
    run_status_enum = sa.Enum("PENDING", "RUNNING", "COMPLETED", "FAILED", name="scheduledreportrunstatus")

    op.create_table(
        "scheduled_ai_reports",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("created_by_user_id", sa.String(), nullable=False),
        sa.Column("institution_id", sa.String(), nullable=True),
        sa.Column("report_type", sa.String(), nullable=False),
        sa.Column("frequency", freq_enum, nullable=False),
        sa.Column("status", status_enum, nullable=False),
        sa.Column("window_days", sa.Integer(), nullable=False),
        sa.Column("focus_areas", sa.JSON(), nullable=False),
        sa.Column("recipients", sa.JSON(), nullable=False),
        sa.Column("timezone", sa.String(), nullable=False),
        sa.Column("time_of_day", sa.String(), nullable=False),
        sa.Column("weekdays", sa.JSON(), nullable=False),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_scheduled_ai_reports_created_by_user_id", "scheduled_ai_reports", ["created_by_user_id"])
    op.create_index("ix_scheduled_ai_reports_institution_id", "scheduled_ai_reports", ["institution_id"])
    op.create_index("ix_scheduled_ai_reports_status", "scheduled_ai_reports", ["status"])
    op.create_index("ix_scheduled_ai_reports_next_run_at", "scheduled_ai_reports", ["next_run_at"])

    op.create_table(
        "scheduled_ai_report_runs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("schedule_id", sa.String(), nullable=False),
        sa.Column("ai_generation_id", sa.String(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", run_status_enum, nullable=False),
        sa.Column("error_details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["schedule_id"], ["scheduled_ai_reports.id"]),
        sa.ForeignKeyConstraint(["ai_generation_id"], ["ai_generations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_scheduled_ai_report_runs_schedule_id", "scheduled_ai_report_runs", ["schedule_id"])
    op.create_index("ix_scheduled_ai_report_runs_ai_generation_id", "scheduled_ai_report_runs", ["ai_generation_id"])
    op.create_index("ix_scheduled_ai_report_runs_due_at", "scheduled_ai_report_runs", ["due_at"])
    op.create_index("ix_scheduled_ai_report_runs_status", "scheduled_ai_report_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_scheduled_ai_report_runs_status", table_name="scheduled_ai_report_runs")
    op.drop_index("ix_scheduled_ai_report_runs_due_at", table_name="scheduled_ai_report_runs")
    op.drop_index("ix_scheduled_ai_report_runs_ai_generation_id", table_name="scheduled_ai_report_runs")
    op.drop_index("ix_scheduled_ai_report_runs_schedule_id", table_name="scheduled_ai_report_runs")
    op.drop_table("scheduled_ai_report_runs")

    op.drop_index("ix_scheduled_ai_reports_next_run_at", table_name="scheduled_ai_reports")
    op.drop_index("ix_scheduled_ai_reports_status", table_name="scheduled_ai_reports")
    op.drop_index("ix_scheduled_ai_reports_institution_id", table_name="scheduled_ai_reports")
    op.drop_index("ix_scheduled_ai_reports_created_by_user_id", table_name="scheduled_ai_reports")
    op.drop_table("scheduled_ai_reports")

