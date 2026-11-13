"""Add the shared 13-table MVP baseline, retaining all legacy data.

The versioned snapshot/backfill modules are immutable migration dependencies.
No live ORM imports, Google calls or migrations at application startup.
"""
import sqlalchemy as sa
from alembic import op
from app.schema_v1 import metadata
from app.backfill_v1 import backfill

revision = '0005'
down_revision = '0004'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    roots = ('orders', 'complaints')
    existing = {}
    for name in roots:
        existing[name] = {c['name'] for c in inspector.get_check_constraints(name)}
        existing[name] |= {c['name'] for c in inspector.get_foreign_keys(name)}
        existing[name] |= {c['name'] for c in inspector.get_unique_constraints(name)}
        column_names = {c['name'] for c in inspector.get_columns(name)}
        for column in metadata.tables[name].columns:
            if column.name not in column_names:
                op.add_column(name, column._copy())
    op.alter_column('complaints', 'processing_error', existing_type=sa.String(80), type_=sa.String(100))
    for name in ('missing_information', 'verification_status', 'case_status'):
        op.alter_column('complaints', name, server_default=metadata.tables['complaints'].c[name].server_default.arg)

    # Create tables first, then FKs (including cyclic same-case pointers).
    for table in metadata.tables.values():
        if table.name not in roots:
            connection.execute(sa.schema.CreateTable(table, include_foreign_key_constraints=[]))
    for table in metadata.tables.values():
        for constraint in sorted(table.foreign_key_constraints, key=lambda c: c.name):
            if constraint.name not in existing.get(table.name, set()):
                connection.execute(sa.schema.AddConstraint(constraint))

    backfill(connection)
    # Flush deferred FK trigger events before adding checks/indexes in this
    # transaction; PostgreSQL rejects ALTER TABLE with pending trigger events.
    connection.execute(sa.text('SET CONSTRAINTS ALL IMMEDIATE'))
    for name in roots:
        table = metadata.tables[name]
        for constraint in sorted(table.constraints, key=lambda c: c.name or ''):
            if isinstance(constraint, (sa.CheckConstraint, sa.UniqueConstraint)) and constraint.name not in existing[name]:
                connection.execute(sa.schema.AddConstraint(constraint))
    for table in metadata.tables.values():
        old_indexes = {i['name'] for i in inspector.get_indexes(table.name)} if table.name in roots else set()
        for index in sorted(table.indexes, key=lambda i: i.name):
            if index.name not in old_indexes:
                connection.execute(sa.schema.CreateIndex(index))


def downgrade():
    raise RuntimeError('0005 retains business history. Restore a verified backup or use a reviewed forward migration; destructive downgrade is disabled.')
