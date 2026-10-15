"""initial durable audit records"""

import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("fields", sa.JSON(), nullable=False),
        sa.Column("lines", sa.JSON(), nullable=False),
        sa.Column("provenance", sa.JSON(), nullable=False),
    )
    op.create_table(
        "audits",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("po_document_id", sa.String(), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("target_document_id", sa.String(), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("findings", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audits")
    op.drop_table("documents")
