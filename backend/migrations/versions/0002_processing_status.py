"""Distinguish analysis in progress from failed analysis."""
from alembic import op
import sqlalchemy as sa
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def replace_constraint(statuses):
    for check in sa.inspect(op.get_bind()).get_check_constraints('complaints'):
        if 'case_status' in check['sqltext']:
            op.drop_constraint(check['name'], 'complaints', type_='check')
    allowed = ','.join("'" + status + "'" for status in statuses)
    op.create_check_constraint('ck_complaints_case_status', 'complaints', 'case_status IN (' + allowed + ')')


def upgrade():
    replace_constraint(['processing','pending_review','insufficient_information','processing_failed','processed'])
    op.execute("UPDATE complaints SET case_status='processing' WHERE case_status='processing_failed' AND processing_error IS NULL")


def downgrade():
    op.execute("UPDATE complaints SET case_status='processing_failed', processing_error='analysis_interrupted_retry_sync' WHERE case_status='processing'")
    replace_constraint(['pending_review','insufficient_information','processing_failed','processed'])
