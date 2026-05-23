"""add idempotency_key to ai_generations

Revision ID: 20260421_0001
Revises: 20260419_0001
Create Date: 2026-04-21 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260421_0001'
down_revision = '20260419_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ai_generations', sa.Column('idempotency_key', sa.String(), nullable=True))
    op.create_index(op.f('ix_ai_generations_idempotency_key'), 'ai_generations', ['idempotency_key'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_ai_generations_idempotency_key'), table_name='ai_generations')
    op.drop_column('ai_generations', 'idempotency_key')
