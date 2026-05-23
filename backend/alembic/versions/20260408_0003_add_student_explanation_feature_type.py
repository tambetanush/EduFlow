"""add student explanation ai feature type

Revision ID: 20260408_0003
Revises: 20260408_0002
Create Date: 2026-04-08 14:35:00.000000
"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "20260408_0003"
down_revision = "20260408_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name if bind is not None else ""

    # PostgreSQL enum type was created by earlier migration as "aifeaturetype".
    # SQLite stores enums as text and does not need type alteration.
    if dialect_name == "postgresql":
        op.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_enum e
                    JOIN pg_type t ON e.enumtypid = t.oid
                    WHERE t.typname = 'aifeaturetype'
                      AND e.enumlabel = 'STUDENT_EXPLANATION'
                ) THEN
                    ALTER TYPE aifeaturetype ADD VALUE 'STUDENT_EXPLANATION';
                END IF;
            END
            $$;
            """
        )


def downgrade() -> None:
    # Enum value removal is intentionally skipped for compatibility.
    pass
