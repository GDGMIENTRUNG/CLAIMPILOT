"""Initial order and complaint schema."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('orders',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('order_id',sa.String(100),nullable=False,unique=True),
        sa.Column('customer_email',sa.String(320),nullable=False),
        sa.Column('order_status',sa.String(40),nullable=False),
        sa.Column('expected_delivery_date',sa.Date()),
        sa.Column('actual_delivery_date',sa.Date()),
        sa.Column('shipping_fee',sa.Numeric(14,2),nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.CheckConstraint('shipping_fee >= 0'),
    )
    op.create_table('complaints',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('gmail_message_id',sa.String(200),nullable=False,unique=True),
        sa.Column('sender_email',sa.String(320),nullable=False),
        sa.Column('email_subject',sa.Text(),nullable=False),
        sa.Column('email_body',sa.Text(),nullable=False),
        sa.Column('received_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('complaint_type',sa.String(40)),
        sa.Column('order_id',sa.String(100)),
        sa.Column('verified_order_id',sa.Integer(),sa.ForeignKey('orders.id')),
        sa.Column('requested_action',sa.String(40)),
        sa.Column('ai_summary',sa.Text()),
        sa.Column('missing_information',postgresql.JSONB(),nullable=False),
        sa.Column('priority',sa.String(10)),
        sa.Column('verification_status',sa.String(40),nullable=False),
        sa.Column('sender_matches_order',sa.Boolean()),
        sa.Column('policy_result',sa.String(40)),
        sa.Column('policy_reason',sa.Text()),
        sa.Column('case_status',sa.String(40),nullable=False),
        sa.Column('processing_error',sa.String(80)),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False,server_default=sa.func.now()),
        sa.CheckConstraint("case_status IN ('pending_review','insufficient_information','processing_failed','processed')"),
        sa.CheckConstraint("priority IS NULL OR priority IN ('low','medium','high')"),
    )
    for column in ['received_at','complaint_type','case_status']:
        op.create_index('ix_complaints_'+column,'complaints',[column])

def downgrade():
    op.drop_table('complaints')
    op.drop_table('orders')
