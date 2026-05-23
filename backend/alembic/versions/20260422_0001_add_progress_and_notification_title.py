"""add notification title and student progress table

Revision ID: 20260422_0001
Revises: 20260421_0001
Create Date: 2026-04-22 00:01:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260422_0001"
down_revision = "20260421_0001"
branch_labels = None
depends_on = None


notification_type_enum = sa.Enum(
    "INFO",
    "SUCCESS",
    "WARNING",
    "GENERAL",
    "TEST",
    "FEES",
    "ATTENDANCE",
    "CERTIFICATE",
    name="notificationtype",
)


def upgrade() -> None:
    op.add_column(
        "notifications",
        sa.Column("title", sa.String(), nullable=True, server_default="Notification"),
    )

    bind = op.get_bind()
    notification_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "student_progress",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("student_id", sa.String(), nullable=False),
        sa.Column("workshop_id", sa.String(), nullable=False),
        sa.Column("current_module_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["workshop_id"], ["workshops.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("student_progress")
    op.drop_column("notifications", "title")
