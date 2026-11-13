"""Immutable CLAIMPILOT_MVP_DB_V1 snapshot used by revision 0005.

Do not edit this snapshot after release: future schema changes need a new revision.
This is executable metadata, not a runtime dependency on the Markdown dictionary.
"""
from uuid import uuid4
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

metadata = sa.MetaData()

orders = sa.Table('orders', metadata,
    sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
    sa.Column('order_id', sa.String(100), nullable=False),
    sa.Column('customer_email', sa.String(320), nullable=False),
    sa.Column('order_status', sa.String(40), nullable=False),
    sa.Column('expected_delivery_date', sa.Date(), nullable=True),
    sa.Column('actual_delivery_date', sa.Date(), nullable=True),
    sa.Column('shipping_fee', sa.Numeric(14, 2), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.Column('purchased_at', sa.Date(), nullable=True),
    sa.Column('product_name', sa.String(200), nullable=True),
    sa.Column('total_amount', sa.Numeric(14, 2), nullable=True),
    sa.Column('currency', sa.CHAR(3), nullable=False, server_default=sa.text("'VND'")),
)

complaints = sa.Table('complaints', metadata,
    sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=True),
    sa.Column('gmail_message_id', sa.String(200), nullable=False),
    sa.Column('sender_email', sa.String(320), nullable=False),
    sa.Column('email_subject', sa.Text(), nullable=False),
    sa.Column('email_body', sa.Text(), nullable=False),
    sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_complaint', sa.Boolean(), nullable=True),
    sa.Column('complaint_type', sa.String(40), nullable=True),
    sa.Column('order_id', sa.String(100), nullable=True),
    sa.Column('verified_order_id', sa.Integer(), nullable=True),
    sa.Column('requested_action', sa.String(40), nullable=True),
    sa.Column('ai_summary', sa.Text(), nullable=True),
    sa.Column('missing_information', pg.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    sa.Column('priority', sa.String(10), nullable=True),
    sa.Column('verification_status', sa.String(40), nullable=False, server_default=sa.text("'not_checked'")),
    sa.Column('sender_matches_order', sa.Boolean(), nullable=True),
    sa.Column('policy_result', sa.String(40), nullable=True),
    sa.Column('policy_reason', sa.Text(), nullable=True),
    sa.Column('case_status', sa.String(40), nullable=False, server_default=sa.text("'processing'")),
    sa.Column('processing_error', sa.String(100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), onupdate=sa.func.now()),
    sa.Column('canonical_case_id', sa.Integer(), nullable=True),
    sa.Column('gmail_thread_id', sa.String(200), nullable=True),
    sa.Column('workflow_status', sa.String(32), nullable=False, server_default=sa.text("'needs_review'")),
    sa.Column('processing_status', sa.String(16), nullable=False, server_default=sa.text("'pending'")),
    sa.Column('ownership_status', sa.String(24), nullable=False, server_default=sa.text("'unverified'")),
    sa.Column('case_version', sa.Integer(), nullable=False, server_default=sa.text('1')),
    sa.Column('current_decision_id', pg.UUID(as_uuid=True), nullable=True),
    sa.Column('latest_text_analysis_id', pg.UUID(as_uuid=True), nullable=True),
    sa.Column('policy_version', sa.String(60), nullable=True),
    sa.Column('policy_snapshot', pg.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    sa.Column('needs_manual_review', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    sa.Column('fulfillment_status', sa.String(16), nullable=False, server_default=sa.text("'not_required'")),
    sa.Column('fulfillment_completed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('fulfillment_completed_by', sa.String(100), nullable=True),
    sa.Column('fulfillment_reference', sa.String(200), nullable=True),
    sa.Column('fulfillment_note', sa.String(2000), nullable=True),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('closed_by', sa.String(100), nullable=True),
    sa.Column('close_note', sa.String(2000), nullable=True),
)

case_messages = sa.Table('case_messages', metadata,
    sa.Column('id', pg.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid4),
    sa.Column('complaint_id', sa.Integer(), nullable=False),
    sa.Column('gmail_message_id', sa.String(200), nullable=False),
    sa.Column('gmail_thread_id', sa.String(200), nullable=True),
    sa.Column('rfc_message_id', sa.Text(), nullable=True),
    sa.Column('in_reply_to', sa.Text(), nullable=True),
    sa.Column('references_header', sa.Text(), nullable=True),
    sa.Column('direction', sa.String(10), nullable=False),
    sa.Column('sender_email', sa.String(320), nullable=False),
    sa.Column('recipient_email', sa.String(320), nullable=True),
    sa.Column('subject', sa.Text(), nullable=False),
    sa.Column('body', sa.Text(), nullable=False),
    sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('processing_status', sa.String(16), nullable=False, server_default=sa.text("'pending'")),
    sa.Column('analysis', pg.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    sa.Column('processing_error', sa.String(100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
)

text_analysis_runs = sa.Table('text_analysis_runs', metadata,
    sa.Column('id', pg.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid4),
    sa.Column('complaint_id', sa.Integer(), nullable=False),
    sa.Column('message_id', pg.UUID(as_uuid=True), nullable=False),
    sa.Column('basis_case_version', sa.Integer(), nullable=False),
    sa.Column('applied_case_version', sa.Integer(), nullable=True),
    sa.Column('provider', sa.String(60), nullable=False),
    sa.Column('model', sa.String(200), nullable=True),
    sa.Column('status', sa.String(16), nullable=False, server_default=sa.text("'processing'")),
    sa.Column('input_hash', sa.CHAR(64), nullable=False),
    sa.Column('input_snapshot', pg.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    sa.Column('output', pg.JSONB(), nullable=True),
    sa.Column('error_code', sa.String(100), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
)

complaint_decisions = sa.Table('complaint_decisions', metadata,
    sa.Column('id', pg.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid4),
    sa.Column('complaint_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(30), nullable=False),
    sa.Column('resolution', sa.String(40), nullable=False),
    sa.Column('note', sa.String(2000), nullable=False),
    sa.Column('missing_fields', pg.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    sa.Column('actor', sa.String(100), nullable=False),
    sa.Column('basis_case_version', sa.Integer(), nullable=False),
    sa.Column('assessment_snapshot', pg.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    sa.Column('proposed_amount', sa.Numeric(14, 2), nullable=True),
    sa.Column('currency', sa.CHAR(3), nullable=False, server_default=sa.text("'VND'")),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
)

case_replies = sa.Table('case_replies', metadata,
    sa.Column('id', pg.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid4),
    sa.Column('complaint_id', sa.Integer(), nullable=False),
    sa.Column('decision_id', pg.UUID(as_uuid=True), nullable=False),
    sa.Column('in_reply_to_message_id', pg.UUID(as_uuid=True), nullable=False),
    sa.Column('recipient_email', sa.String(320), nullable=False),
    sa.Column('subject', sa.String(300), nullable=False),
    sa.Column('body', sa.Text(), nullable=False, server_default=sa.text("''")),
    sa.Column('status', sa.String(20), nullable=False, server_default=sa.text("'prepared'")),
    sa.Column('basis_case_version', sa.Integer(), nullable=False),
    sa.Column('revision', sa.Integer(), nullable=False, server_default=sa.text('1')),
    sa.Column('gmail_draft_id', sa.String(200), nullable=True),
    sa.Column('gmail_draft_content_hash', sa.CHAR(64), nullable=True),
    sa.Column('accepted_external_hash', sa.CHAR(64), nullable=True),
    sa.Column('gmail_sent_message_id', sa.String(200), nullable=True),
    sa.Column('sent_message_id', pg.UUID(as_uuid=True), nullable=True),
    sa.Column('outbound_rfc_message_id', sa.Text(), nullable=False),
    sa.Column('operation', sa.String(12), nullable=True),
    sa.Column('attempt_token', pg.UUID(as_uuid=True), nullable=True),
    sa.Column('error_code', sa.String(100), nullable=True),
    sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), onupdate=sa.func.now()),
)

reply_operations = sa.Table('reply_operations', metadata,
    sa.Column('id', pg.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid4),
    sa.Column('reply_id', pg.UUID(as_uuid=True), nullable=False),
    sa.Column('idempotency_key', pg.UUID(as_uuid=True), nullable=False),
    sa.Column('operation', sa.String(12), nullable=False),
    sa.Column('expected_case_version', sa.Integer(), nullable=False),
    sa.Column('expected_revision', sa.Integer(), nullable=False),
    sa.Column('request_hash', sa.CHAR(64), nullable=False),
    sa.Column('request_snapshot', pg.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    sa.Column('result_snapshot', pg.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    sa.Column('actor', sa.String(100), nullable=False),
    sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('confirmed_by', sa.String(100), nullable=True),
    sa.Column('status', sa.String(20), nullable=False, server_default=sa.text("'in_progress'")),
    sa.Column('error_code', sa.String(100), nullable=True),
    sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
)

audit_events = sa.Table('audit_events', metadata,
    sa.Column('id', pg.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid4),
    sa.Column('complaint_id', sa.Integer(), nullable=False),
    sa.Column('event_type', sa.String(60), nullable=False),
    sa.Column('actor', sa.String(100), nullable=False),
    sa.Column('before_data', pg.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    sa.Column('after_data', pg.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    sa.Column('note', sa.String(2000), nullable=False, server_default=sa.text("''")),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
)

evidence_assets = sa.Table('evidence_assets', metadata,
    sa.Column('id', pg.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid4),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('message_id', pg.UUID(as_uuid=True), nullable=True),
    sa.Column('source', sa.String(12), nullable=False),
    sa.Column('evidence_kind', sa.String(20), nullable=False),
    sa.Column('bucket_name', sa.String(222), nullable=False),
    sa.Column('object_key', sa.String(1024), nullable=False),
    sa.Column('object_generation', sa.BigInteger(), nullable=False),
    sa.Column('content_type', sa.String(30), nullable=False),
    sa.Column('size_bytes', sa.Integer(), nullable=False),
    sa.Column('width_px', sa.Integer(), nullable=False),
    sa.Column('height_px', sa.Integer(), nullable=False),
    sa.Column('sha256', sa.CHAR(64), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
)

evidence_analyses = sa.Table('evidence_analyses', metadata,
    sa.Column('id', pg.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid4),
    sa.Column('complaint_id', sa.Integer(), nullable=False),
    sa.Column('basis_case_version', sa.Integer(), nullable=False),
    sa.Column('applied_case_version', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(16), nullable=False, server_default=sa.text("'pending'")),
    sa.Column('mode', sa.String(16), nullable=False),
    sa.Column('asset_ids', pg.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    sa.Column('provider', sa.String(60), nullable=False, server_default=sa.text("'gemini'")),
    sa.Column('model', sa.String(200), nullable=True),
    sa.Column('consistency', sa.String(20), nullable=True),
    sa.Column('observations', pg.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    sa.Column('limitations', pg.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    sa.Column('missing_evidence', pg.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    sa.Column('error_code', sa.String(100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
)

staff_sessions = sa.Table('staff_sessions', metadata,
    sa.Column('id', pg.UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid4),
    sa.Column('token_hash', sa.CHAR(64), nullable=False),
    sa.Column('csrf_hash', sa.CHAR(64), nullable=False),
    sa.Column('staff_id', sa.String(100), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
)

integration_state = sa.Table('integration_state', metadata,
    sa.Column('id', sa.Integer(), nullable=False, primary_key=True, autoincrement=False),
    sa.Column('mailbox_email', sa.String(320), nullable=True),
    sa.Column('last_attempt_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_error_code', sa.String(100), nullable=True),
    sa.Column('last_duration_ms', sa.Integer(), nullable=True),
    sa.Column('pending_thread_ids', pg.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
    sa.Column('known_thread_cursor', sa.Integer(), nullable=False, server_default=sa.text('0')),
    sa.Column('discovery_page_token', sa.Text(), nullable=True),
    sa.Column('deferred_count', sa.Integer(), nullable=False, server_default=sa.text('0')),
    sa.Column('last_sync_summary', pg.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()'), onupdate=sa.func.now()),
)

gmail_intake_failures = sa.Table('gmail_intake_failures', metadata,
    sa.Column('gmail_message_id', sa.String(200), nullable=False, primary_key=True),
    sa.Column('gmail_thread_id', sa.String(200), nullable=True),
    sa.Column('complaint_id', sa.Integer(), nullable=True),
    sa.Column('error_code', sa.String(100), nullable=False),
    sa.Column('status', sa.String(12), nullable=False, server_default=sa.text("'pending'")),
    sa.Column('attempt_count', sa.Integer(), nullable=False, server_default=sa.text('1')),
    sa.Column('first_seen_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.Column('last_attempt_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('resolved_by', sa.String(100), nullable=True),
    sa.Column('resolution_note', sa.String(2000), nullable=True),
)


def _check(table, name, expression):
    table.append_constraint(sa.CheckConstraint(expression, name=name))


def _enum(table, column, values):
    allowed = ','.join(repr(v) for v in values.split())
    _check(table, f'ck_{table.name}_{column}', f'{column} IN ({allowed})')


def _unique(table, name, *columns):
    table.append_constraint(sa.UniqueConstraint(*columns, name=name))


def _fk(table, name, columns, target, remote, deferred=False):
    table.append_constraint(sa.ForeignKeyConstraint(
        columns, [f'{target}.{c}' for c in remote], name=name,
        deferrable=True if deferred else None,
        initially='DEFERRED' if deferred else None, use_alter=deferred,
    ))


def _index(table, name, *columns, where=None, unique=False):
    expressions = [table.c[c[:-5]].desc() if c.endswith(' DESC') else table.c[c] for c in columns]
    sa.Index(name, *expressions, unique=unique,
             postgresql_where=sa.text(where) if where else None)


# Legacy names stay stable; indexes/constraints are never dropped for convenience.
_unique(orders, 'orders_order_id_key', 'order_id')
_unique(complaints, 'complaints_gmail_message_id_key', 'gmail_message_id')
_check(orders, 'orders_shipping_fee_check', 'shipping_fee >= 0')
_check(orders, 'ck_orders_total_amount', 'total_amount IS NULL OR total_amount >= 0')
_check(orders, 'ck_orders_currency', "currency = 'VND'")
_check(complaints, 'complaints_priority_check', "priority IS NULL OR priority IN ('low','medium','high')")
_enum(complaints, 'case_status', 'processing pending_review insufficient_information processing_failed processed')
_enum(complaints, 'workflow_status', 'needs_review waiting_customer waiting_fulfillment resolved closed')
_enum(complaints, 'processing_status', 'pending processing completed failed')
_enum(complaints, 'ownership_status', 'unverified email_matched manually_verified mismatch')
_enum(complaints, 'complaint_type', 'late_delivery not_received damaged_item wrong_item refund_request other')
_enum(complaints, 'requested_action', 'shipping_fee_refund order_refund replacement request_information other')
_enum(complaints, 'policy_result', 'eligible_for_review not_eligible insufficient_information order_not_found not_applicable')
_enum(complaints, 'fulfillment_status', 'not_required pending completed')
_check(complaints, 'ck_cases_version', 'case_version >= 1')
_check(complaints, 'ck_cases_canonical', 'canonical_case_id IS NULL OR canonical_case_id <> id')
_check(complaints, 'ck_cases_closed', """
    (workflow_status = 'closed' AND closed_at IS NOT NULL AND closed_by IS NOT NULL
     AND length(btrim(closed_by)) > 0 AND close_note IS NOT NULL AND length(btrim(close_note)) > 0)
    OR (workflow_status <> 'closed' AND closed_at IS NULL AND closed_by IS NULL AND close_note IS NULL)
""")
_check(complaints, 'ck_cases_resolved', """
    (workflow_status IN ('resolved','closed') AND resolved_at IS NOT NULL)
    OR (workflow_status NOT IN ('resolved','closed') AND resolved_at IS NULL)
""")
_check(complaints, 'ck_cases_fulfillment', """
    (fulfillment_status = 'completed' AND fulfillment_completed_at IS NOT NULL
     AND fulfillment_completed_by IS NOT NULL AND length(btrim(fulfillment_completed_by)) > 0
     AND fulfillment_note IS NOT NULL AND length(btrim(fulfillment_note)) > 0)
    OR (fulfillment_status <> 'completed' AND fulfillment_completed_at IS NULL
        AND fulfillment_completed_by IS NULL AND fulfillment_reference IS NULL AND fulfillment_note IS NULL)
""")

_unique(case_messages, 'uq_messages_gmail', 'gmail_message_id')
_unique(case_messages, 'uq_messages_case', 'id', 'complaint_id')
_enum(case_messages, 'direction', 'inbound outbound')
_enum(case_messages, 'processing_status', 'pending processing completed failed')
_check(case_messages, 'ck_messages_outbound', "direction <> 'outbound' OR (recipient_email IS NOT NULL AND length(btrim(recipient_email)) > 0 AND processing_status = 'completed')")

_unique(text_analysis_runs, 'uq_text_runs_case', 'id', 'complaint_id')
_enum(text_analysis_runs, 'status', 'processing completed failed stale')
_check(text_analysis_runs, 'ck_text_runs_versions', 'basis_case_version >= 1 AND (applied_case_version IS NULL OR applied_case_version >= basis_case_version)')
_check(text_analysis_runs, 'ck_text_runs_completion', """
    (status = 'processing' AND finished_at IS NULL AND applied_case_version IS NULL)
    OR (status = 'completed' AND finished_at IS NOT NULL AND output IS NOT NULL AND applied_case_version IS NOT NULL)
    OR (status = 'stale' AND finished_at IS NOT NULL AND output IS NOT NULL AND applied_case_version IS NULL)
    OR (status = 'failed' AND finished_at IS NOT NULL AND error_code IS NOT NULL AND length(btrim(error_code)) > 0 AND applied_case_version IS NULL)
""")
_check(text_analysis_runs, 'ck_text_runs_time', 'finished_at IS NULL OR finished_at >= started_at')

_unique(complaint_decisions, 'uq_decisions_case', 'id', 'complaint_id')
_unique(complaint_decisions, 'uq_decisions_basis', 'complaint_id', 'basis_case_version')
_enum(complaint_decisions, 'action', 'approve reject request_information')
_enum(complaint_decisions, 'resolution', 'shipping_fee_refund order_refund replacement reshipment carrier_investigation decline request_information other')
_check(complaint_decisions, 'ck_decisions_note', 'length(btrim(note)) BETWEEN 1 AND 2000')
_check(complaint_decisions, 'ck_decisions_version', 'basis_case_version >= 1')
_check(complaint_decisions, 'ck_decisions_currency', "currency = 'VND'")
_check(complaint_decisions, 'ck_decisions_amount', "proposed_amount IS NULL OR (proposed_amount >= 0 AND action = 'approve' AND resolution IN ('shipping_fee_refund','order_refund'))")
_check(complaint_decisions, 'ck_decisions_resolution', """
    CASE WHEN jsonb_typeof(missing_fields) = 'array' THEN
      (action = 'request_information' AND resolution = 'request_information' AND jsonb_array_length(missing_fields) BETWEEN 1 AND 20)
      OR (action = 'reject' AND resolution = 'decline' AND jsonb_array_length(missing_fields) = 0)
      OR (action = 'approve' AND resolution IN ('shipping_fee_refund','order_refund','replacement','reshipment','carrier_investigation','other') AND jsonb_array_length(missing_fields) = 0)
    ELSE false END
""")

for column in ('decision_id', 'gmail_sent_message_id', 'outbound_rfc_message_id'):
    _unique(case_replies, f'uq_replies_{column}', column)
_enum(case_replies, 'status', 'prepared draft_saving draft_saved sending sent failed unknown')
_enum(case_replies, 'operation', 'save_draft send')
_check(case_replies, 'ck_replies_versions', 'basis_case_version >= 1 AND revision >= 1')
_check(case_replies, 'ck_replies_subject', "length(btrim(subject)) BETWEEN 1 AND 300 AND position(chr(10) in subject) = 0 AND position(chr(13) in subject) = 0")
_check(case_replies, 'ck_replies_body', 'length(body) <= 10000')
_check(case_replies, 'ck_replies_sent', """
    (status = 'sent' AND gmail_sent_message_id IS NOT NULL AND sent_message_id IS NOT NULL AND sent_at IS NOT NULL)
    OR (status <> 'sent' AND gmail_sent_message_id IS NULL AND sent_message_id IS NULL AND sent_at IS NULL)
""")
_check(case_replies, 'ck_replies_draft', "status <> 'draft_saved' OR gmail_draft_id IS NOT NULL")
_check(case_replies, 'ck_replies_busy', "status NOT IN ('sending','draft_saving') OR (attempt_token IS NOT NULL AND operation IS NOT NULL AND ((status = 'sending' AND operation = 'send') OR (status = 'draft_saving' AND operation = 'save_draft')))")

_unique(reply_operations, 'uq_operations_key', 'idempotency_key')
_unique(reply_operations, 'uq_operations_reply', 'id', 'reply_id')
_enum(reply_operations, 'operation', 'save_draft send')
_enum(reply_operations, 'status', 'in_progress succeeded failed unknown')
_check(reply_operations, 'ck_operations_versions', 'expected_case_version >= 1 AND expected_revision >= 1')
_check(reply_operations, 'ck_operations_confirm', "operation <> 'send' OR (confirmed_at IS NOT NULL AND confirmed_by IS NOT NULL AND confirmed_by = actor)")
_check(reply_operations, 'ck_operations_finished', "(status = 'in_progress' AND finished_at IS NULL) OR (status <> 'in_progress' AND finished_at IS NOT NULL AND finished_at >= started_at)")
_check(reply_operations, 'ck_operations_error', "status NOT IN ('failed','unknown') OR (error_code IS NOT NULL AND length(btrim(error_code)) > 0)")
_check(audit_events, 'ck_audit_note', 'length(note) <= 2000')

_unique(evidence_assets, 'uq_assets_location', 'bucket_name', 'object_key', 'object_generation')
_enum(evidence_assets, 'source', 'order customer')
_enum(evidence_assets, 'evidence_kind', 'packing delivery customer')
_enum(evidence_assets, 'content_type', 'image/jpeg image/png')
_check(evidence_assets, 'ck_assets_owner', "(source = 'order' AND order_id IS NOT NULL AND message_id IS NULL AND evidence_kind IN ('packing','delivery')) OR (source = 'customer' AND message_id IS NOT NULL AND order_id IS NULL AND evidence_kind = 'customer')")
_check(evidence_assets, 'ck_assets_size', 'size_bytes BETWEEN 1 AND 5242880')
_check(evidence_assets, 'ck_assets_dimensions', 'width_px > 0 AND height_px > 0 AND width_px::bigint * height_px <= 20000000')
_check(evidence_assets, 'ck_assets_generation', 'object_generation > 0')

_enum(evidence_analyses, 'status', 'pending completed failed')
_enum(evidence_analyses, 'mode', 'single_side comparison')
_enum(evidence_analyses, 'consistency', 'consistent inconsistent inconclusive')
_check(evidence_analyses, 'ck_evidence_versions', 'basis_case_version >= 1 AND (applied_case_version IS NULL OR applied_case_version >= basis_case_version)')
_check(evidence_analyses, 'ck_evidence_assets', "CASE WHEN jsonb_typeof(asset_ids) = 'array' THEN jsonb_array_length(asset_ids) BETWEEN 1 AND 4 ELSE false END")
_check(evidence_analyses, 'ck_evidence_completion', """
    (status = 'pending' AND completed_at IS NULL AND applied_case_version IS NULL)
    OR (status = 'completed' AND completed_at IS NOT NULL AND completed_at >= created_at AND consistency IS NOT NULL AND (mode <> 'single_side' OR consistency = 'inconclusive'))
    OR (status = 'failed' AND completed_at IS NOT NULL AND completed_at >= created_at AND error_code IS NOT NULL AND length(btrim(error_code)) > 0 AND applied_case_version IS NULL)
""")

_unique(staff_sessions, 'uq_sessions_token', 'token_hash')
_check(staff_sessions, 'ck_sessions_expiry', 'expires_at > created_at AND (revoked_at IS NULL OR revoked_at >= created_at)')
_check(integration_state, 'ck_integration_singleton', 'id = 1')
_check(integration_state, 'ck_integration_counts', 'known_thread_cursor >= 0 AND deferred_count >= 0 AND (last_duration_ms IS NULL OR last_duration_ms >= 0)')
_enum(gmail_intake_failures, 'status', 'pending resolved ignored')
_check(gmail_intake_failures, 'ck_intake_attempts', 'attempt_count >= 1 AND last_attempt_at >= first_seen_at')
_check(gmail_intake_failures, 'ck_intake_resolution', """
    (status = 'pending' AND resolved_at IS NULL AND resolved_by IS NULL AND resolution_note IS NULL)
    OR (status IN ('resolved','ignored') AND resolved_at IS NOT NULL AND resolved_at >= first_seen_at
        AND resolved_by IS NOT NULL AND length(btrim(resolved_by)) > 0
        AND (status <> 'ignored' OR (resolution_note IS NOT NULL AND length(btrim(resolution_note)) > 0)))
""")

# JSON shape and digest checks deliberately avoid PostgreSQL UNKNOWN loopholes.
for table, columns, shape in [
    (complaints, ['missing_information'], 'array'), (complaints, ['policy_snapshot'], 'object'),
    (case_messages, ['analysis'], 'object'),
    (text_analysis_runs, ['input_snapshot', 'output'], 'object'),
    (complaint_decisions, ['missing_fields'], 'array'),
    (complaint_decisions, ['assessment_snapshot'], 'object'),
    (reply_operations, ['request_snapshot', 'result_snapshot'], 'object'),
    (audit_events, ['before_data', 'after_data'], 'object'),
    (evidence_analyses, ['asset_ids', 'observations', 'limitations', 'missing_evidence'], 'array'),
    (integration_state, ['pending_thread_ids'], 'array'),
    (integration_state, ['last_sync_summary'], 'object'),
]:
    for column in columns:
        _check(table, f'ck_{table.name}_{column}_json', f"{column} IS NULL OR jsonb_typeof({column}) = '{shape}'" if table.c[column].nullable else f"jsonb_typeof({column}) = '{shape}'")
for table, columns in [
    (text_analysis_runs, ['input_hash']), (reply_operations, ['request_hash']),
    (case_replies, ['gmail_draft_content_hash', 'accepted_external_hash']),
    (evidence_assets, ['sha256']), (staff_sessions, ['token_hash', 'csrf_hash']),
]:
    for column in columns:
        _check(table, f'ck_{table.name}_{column}_hash', f"{column} ~ '^[0-9a-f]{{64}}$'")
for table in (complaint_decisions, reply_operations, audit_events):
    _check(table, f'ck_{table.name}_actor', 'length(btrim(actor)) > 0')

for table in (case_messages, text_analysis_runs, complaint_decisions, case_replies,
              audit_events, evidence_analyses, gmail_intake_failures):
    _fk(table, f'fk_{table.name}_case', ['complaint_id'], 'complaints', ['id'])
_fk(complaints, 'complaints_verified_order_id_fkey', ['verified_order_id'], 'orders', ['id'])
_fk(complaints, 'fk_cases_canonical', ['canonical_case_id'], 'complaints', ['id'])
_fk(complaints, 'fk_cases_current_decision', ['current_decision_id', 'id'], 'complaint_decisions', ['id', 'complaint_id'], True)
_fk(complaints, 'fk_cases_latest_text', ['latest_text_analysis_id', 'id'], 'text_analysis_runs', ['id', 'complaint_id'], True)
_fk(text_analysis_runs, 'fk_text_runs_message', ['message_id', 'complaint_id'], 'case_messages', ['id', 'complaint_id'])
_fk(case_replies, 'fk_replies_decision', ['decision_id', 'complaint_id'], 'complaint_decisions', ['id', 'complaint_id'])
_fk(case_replies, 'fk_replies_inbound', ['in_reply_to_message_id', 'complaint_id'], 'case_messages', ['id', 'complaint_id'])
_fk(case_replies, 'fk_replies_sent', ['sent_message_id', 'complaint_id'], 'case_messages', ['id', 'complaint_id'])
_fk(case_replies, 'fk_replies_attempt', ['attempt_token', 'id'], 'reply_operations', ['id', 'reply_id'], True)
_fk(reply_operations, 'fk_operations_reply', ['reply_id'], 'case_replies', ['id'])
_fk(evidence_assets, 'fk_assets_order', ['order_id'], 'orders', ['id'])
_fk(evidence_assets, 'fk_assets_message', ['message_id'], 'case_messages', ['id'])

_index(complaints, 'uq_complaints_canonical_thread', 'gmail_thread_id', unique=True, where='gmail_thread_id IS NOT NULL AND canonical_case_id IS NULL')
_index(reply_operations, 'uq_reply_operations_unsettled', 'reply_id', unique=True, where="status IN ('in_progress','unknown')")
_index(text_analysis_runs, 'uq_text_runs_active', 'message_id', unique=True, where="status = 'processing'")
_index(evidence_analyses, 'uq_evidence_pending', 'complaint_id', unique=True, where="status = 'pending'")
_index(evidence_assets, 'uq_assets_order_hash', 'order_id', 'evidence_kind', 'sha256', unique=True, where="source = 'order'")
_index(evidence_assets, 'uq_assets_customer_hash', 'message_id', 'sha256', unique=True, where="source = 'customer'")
for column in ('received_at', 'complaint_type', 'case_status', 'is_complaint'):
    _index(complaints, f'ix_complaints_{column}', column)
_index(complaints, 'ix_cases_work_queue', 'workflow_status', 'updated_at DESC', 'id', where='canonical_case_id IS NULL AND is_complaint IS TRUE')
_index(complaints, 'ix_cases_technical_queue', 'processing_status', 'updated_at DESC', 'id', where='canonical_case_id IS NULL AND is_complaint IS DISTINCT FROM FALSE')
_index(complaints, 'ix_cases_order', 'verified_order_id')
_index(complaints, 'ix_cases_alias', 'canonical_case_id', where='canonical_case_id IS NOT NULL')
_index(case_messages, 'ix_messages_timeline', 'complaint_id', 'occurred_at', 'id')
_index(text_analysis_runs, 'ix_text_runs_history', 'complaint_id', 'started_at DESC', 'id')
_index(text_analysis_runs, 'ix_text_runs_message', 'message_id', 'started_at DESC')
_index(complaint_decisions, 'ix_decisions_history', 'complaint_id', 'created_at', 'id')
_index(case_replies, 'ix_replies_case', 'complaint_id', 'created_at', 'id')
_index(reply_operations, 'ix_operations_reply', 'reply_id', 'started_at DESC', 'id')
_index(audit_events, 'ix_audit_history', 'complaint_id', 'created_at', 'id')
_index(evidence_assets, 'ix_assets_order', 'order_id', 'created_at', 'id', where="source = 'order'")
_index(evidence_assets, 'ix_assets_message', 'message_id', 'created_at', 'id', where="source = 'customer'")
_index(evidence_analyses, 'ix_evidence_history', 'complaint_id', 'created_at DESC', 'id')
_index(staff_sessions, 'ix_sessions_expiry', 'expires_at')
_index(gmail_intake_failures, 'ix_intake_pending', 'status', 'last_attempt_at', 'gmail_message_id')
_index(gmail_intake_failures, 'ix_intake_case', 'complaint_id', where='complaint_id IS NOT NULL')
