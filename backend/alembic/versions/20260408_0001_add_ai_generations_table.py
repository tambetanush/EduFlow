"""add ai_generations table

Revision ID: 20260408_0001
Revises:
Create Date: 2026-04-08 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260408_0001"
down_revision = "20260401_0000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    feature_type_enum = sa.Enum("ADMIN_REPORT", name="aifeaturetype")
    status_enum = sa.Enum("PENDING", "PROCESSING", "COMPLETED", "FAILED", name="aigenerationstatus")

    op.create_table(
        "ai_generations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("feature_type", feature_type_enum, nullable=False),
        sa.Column("requester_user_id", sa.String(), nullable=False),
        sa.Column("institution_id", sa.String(), nullable=True),
        sa.Column("source_entity_type", sa.String(), nullable=False),
        sa.Column("source_entity_id", sa.String(), nullable=False),
        sa.Column("request_fingerprint", sa.String(length=64), nullable=False),
        sa.Column("prompt_version", sa.String(), nullable=False),
        sa.Column("model_name", sa.String(), nullable=False),
        sa.Column("raw_prompt_input", sa.JSON(), nullable=False),
        sa.Column("raw_model_output", sa.Text(), nullable=True),
        sa.Column("parsed_output_json", sa.JSON(), nullable=True),
        sa.Column("status", status_enum, nullable=False),
        sa.Column("error_details", sa.JSON(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("cache_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["requester_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_ai_generations_feature_type", "ai_generations", ["feature_type"])
    op.create_index("ix_ai_generations_requester_user_id", "ai_generations", ["requester_user_id"])
    op.create_index("ix_ai_generations_institution_id", "ai_generations", ["institution_id"])
    op.create_index("ix_ai_generations_request_fingerprint", "ai_generations", ["request_fingerprint"])
    op.create_index("ix_ai_generations_status", "ai_generations", ["status"])
    op.create_index(
        "ix_ai_generations_feature_fingerprint_status",
        "ai_generations",
        ["feature_type", "request_fingerprint", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_ai_generations_feature_fingerprint_status", table_name="ai_generations")
    op.drop_index("ix_ai_generations_status", table_name="ai_generations")
    op.drop_index("ix_ai_generations_request_fingerprint", table_name="ai_generations")
    op.drop_index("ix_ai_generations_institution_id", table_name="ai_generations")
    op.drop_index("ix_ai_generations_requester_user_id", table_name="ai_generations")
    op.drop_index("ix_ai_generations_feature_type", table_name="ai_generations")
    op.drop_table("ai_generations")

