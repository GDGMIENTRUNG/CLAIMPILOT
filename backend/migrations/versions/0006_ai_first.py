"""CR-001 local implementation: seven additive tables, existing history retained."""
import sqlalchemy as sa
from alembic import op
from app.schema_v1 import metadata as core
from app.schema_v2 import attach, metadata as extension
revision='0006'
down_revision='0005'
branch_labels=None
depends_on=None

def upgrade():
    target=sa.MetaData()
    for t in core.tables.values(): t.to_metadata(target)
    attach(target)
    bind=op.get_bind()
    for name in extension.tables:
        bind.execute(sa.schema.CreateTable(target.tables[name],include_foreign_key_constraints=[]))
    for name in extension.tables:
        t=target.tables[name]
        for c in t.foreign_key_constraints: bind.execute(sa.schema.AddConstraint(c))
        for i in t.indexes: bind.execute(sa.schema.CreateIndex(i))

def downgrade():
    raise RuntimeError('Restore a verified backup or use a reviewed forward migration; do not delete customer/KB history.')
