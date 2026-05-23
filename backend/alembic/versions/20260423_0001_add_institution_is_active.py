"""add is_active to institutions

Revision ID: 20260423_0001
Revises: 20260422_0001
Create Date: 2026-04-23 00:01:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260423_0001"
down_revision = "20260422_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("institutions") as batch_op:
        batch_op.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade() -> None:
    with op.batch_alter_table("institutions") as batch_op:
        batch_op.drop_column("is_active")