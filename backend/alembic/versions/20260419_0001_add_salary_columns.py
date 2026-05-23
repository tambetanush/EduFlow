"""Add salary columns to users table

Revision ID: 20260419_0001
Revises: 20260417_0005
Create Date: 2024-04-19 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260419_0001'
down_revision = '20260417_0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('salary_amount', sa.Integer(), server_default='0', nullable=True))
    op.add_column('users', sa.Column('salary_type', sa.String(), server_default='monthly', nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'salary_type')
    op.drop_column('users', 'salary_amount')