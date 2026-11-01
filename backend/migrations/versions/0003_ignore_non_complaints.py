"""Store AI complaint classification and hide unrelated email."""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "complaints",
        sa.Column("is_complaint", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_complaints_is_complaint", "complaints", ["is_complaint"])


def downgrade():
    op.drop_index("ix_complaints_is_complaint", table_name="complaints")
    op.drop_column("complaints", "is_complaint")
