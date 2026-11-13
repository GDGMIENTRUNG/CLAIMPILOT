"""Keep unclassified Gmail candidates out of the complaint dashboard."""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "UPDATE complaints SET is_complaint=NULL "
        "WHERE case_status IN ('processing', 'processing_failed')"
    )
    op.alter_column(
        "complaints",
        "is_complaint",
        existing_type=sa.Boolean(),
        nullable=True,
        server_default=None,
    )


def downgrade():
    op.execute("UPDATE complaints SET is_complaint=true WHERE is_complaint IS NULL")
    op.alter_column(
        "complaints",
        "is_complaint",
        existing_type=sa.Boolean(),
        nullable=False,
        server_default=sa.true(),
    )
