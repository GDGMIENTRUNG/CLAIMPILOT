"""Frozen, repeat-safe legacy backfill for revision 0005. No network calls.

Keep independent of live ORM/services so old migrations remain reproducible.
The existing anchor is the per-case completion marker; never reset a live case.
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Literal
from uuid import NAMESPACE_URL, uuid5

import sqlalchemy as sa
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from sqlalchemy.dialects.postgresql import insert
from app.schema_v1 import metadata


class _LegacyAnalysis(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    is_complaint: bool
    complaint_type: Literal['late_delivery', 'not_received', 'damaged_item', 'wrong_item', 'refund_request', 'other']
    order_id: str | None = Field(max_length=100)
    requested_action: Literal['shipping_fee_refund', 'order_refund', 'replacement', 'request_information', 'other']
    summary: str = Field(min_length=1, max_length=4000)
    missing_information: list[str] = Field(max_length=30)
    priority: Literal['low', 'medium', 'high']


def backfill(connection):
    """Run inside the caller's transaction, with intake/mutations stopped.

    Returns counts only, never customer content. 0004 cannot contain thread
    metadata; no thread, recipient, staff decision or Gmail side effect is invented.
    """
    cases = metadata.tables['complaints']
    messages = metadata.tables['case_messages']
    runs = metadata.tables['text_analysis_runs']
    count = 0
    # Stream IDs and reload with a lock: bounded memory and no projection races.
    ids = connection.execute(sa.select(cases.c.id).order_by(cases.c.id)).scalars()
    for case_id in ids:
        with connection.begin_nested():
            row = connection.execute(sa.select(cases).where(cases.c.id == case_id).with_for_update()).mappings().one()
            if connection.scalar(sa.select(messages.c.id).where(messages.c.gmail_message_id == row['gmail_message_id'])):
                continue
            # The helper is repeat-safe on baseline data, but must not merge live
            # workflow state or a later alias. Canonicalization belongs to intake.
            if row['canonical_case_id'] is not None or row['case_version'] != 1 or row['current_decision_id'] is not None or row['workflow_status'] != 'needs_review':
                continue
            status = {'processing': 'processing', 'processing_failed': 'failed'}.get(row['case_status'], 'completed')
            analysis = None
            if status == 'completed':
                try:
                    analysis = _LegacyAnalysis.model_validate({
                        'is_complaint': row['is_complaint'], 'complaint_type': row['complaint_type'],
                        'order_id': row['order_id'], 'requested_action': row['requested_action'],
                        'summary': row['ai_summary'], 'missing_information': row['missing_information'],
                        'priority': row['priority'],
                    }).model_dump()
                except ValidationError:
                    pass
            message_id = uuid5(NAMESPACE_URL, 'claimpilot:legacy-message:' + row['gmail_message_id'])
            connection.execute(messages.insert().values(
                id=message_id, complaint_id=case_id, gmail_message_id=row['gmail_message_id'],
                gmail_thread_id=row['gmail_thread_id'], direction='inbound',
                sender_email=row['sender_email'], recipient_email=None,
                subject=row['email_subject'], body=row['email_body'], occurred_at=row['received_at'],
                processing_status=status, processing_error=row['processing_error'], analysis=analysis or {},
            ))
            values = {'processing_status': status}
            if analysis is not None:
                now = datetime.now(timezone.utc)
                run_id = uuid5(NAMESPACE_URL, 'claimpilot:legacy-text:' + row['gmail_message_id'])
                snapshot = {'source': 'legacy', 'complaint_id': case_id,
                            'message_id': str(message_id), 'basis_case_version': 1}
                digest = hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                connection.execute(runs.insert().values(
                    id=run_id, complaint_id=case_id, message_id=message_id,
                    basis_case_version=1, applied_case_version=1, provider='legacy_unknown',
                    model=None, status='completed', input_hash=digest, input_snapshot=snapshot,
                    output=analysis, started_at=now, finished_at=now,
                ))
                values['latest_text_analysis_id'] = run_id
            # Preserve updated_at, old root fields and the original tri-state.
            values['updated_at'] = row['updated_at']
            connection.execute(cases.update().where(cases.c.id == case_id).values(**values))
            count += 1
    connection.execute(insert(metadata.tables['integration_state']).values(id=1).on_conflict_do_nothing(index_elements=['id']))
    return count
