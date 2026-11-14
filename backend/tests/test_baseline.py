"""PostgreSQL baseline tests. Synthetic data; no Gmail/AI/network side effects."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
from uuid import NAMESPACE_URL, uuid4, uuid5

import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from alembic import command
from alembic.config import Config
from app.database import Base
from app.config import settings
from app.models import Complaint, Order
from app.schema_v1 import metadata
from app.backfill_v1 import backfill

NOW = datetime.now(timezone.utc)


def case(db, suffix='a'):
    row = Complaint(gmail_message_id='synthetic-' + suffix, sender_email='customer@example.test',
                    email_subject='Test', email_body='Synthetic body', received_at=NOW)
    db.add(row)
    db.flush()
    return row


def message(db, complaint_id):
    identifier = uuid4()
    db.execute(metadata.tables['case_messages'].insert().values(
        id=identifier, complaint_id=complaint_id, gmail_message_id=str(identifier),
        direction='inbound', sender_email='customer@example.test',
        subject='Synthetic', body='Test', occurred_at=NOW))
    return identifier


def decision(db, complaint_id):
    identifier = uuid4()
    db.execute(metadata.tables['complaint_decisions'].insert().values(
        id=identifier, complaint_id=complaint_id, action='reject', resolution='decline',
        note='Synthetic review', actor='test-staff', basis_case_version=1))
    return identifier


def reply(db, complaint_id, decision_id, message_id):
    identifier = uuid4()
    db.execute(metadata.tables['case_replies'].insert().values(
        id=identifier, complaint_id=complaint_id, decision_id=decision_id,
        in_reply_to_message_id=message_id, recipient_email='customer@example.test',
        subject='Re: Test', basis_case_version=1, outbound_rfc_message_id=f'<{identifier}@example.test>'))
    return identifier


def rejected(db, statement):
    with pytest.raises(IntegrityError), db.begin_nested():
        db.execute(statement)
        # Also exercise INITIALLY DEFERRED pointer FKs, inside the savepoint.
        db.execute(sa.text('SET CONSTRAINTS ALL IMMEDIATE'))


def test_dictionary_matches_runtime_metadata():
    source = (Path(__file__).resolve().parents[2] / 'docs/DATABASE_DESIGN.md').read_text()
    blocks = re.split(r'^### 6\.\d+\. `(\w+)`\s*$', source, flags=re.M)
    documented = {}
    for i in range(1, len(blocks), 2):
        fields = {}
        for line in blocks[i + 1].splitlines():
            cells = [v.strip() for v in line.strip('|').split('|')]
            if len(cells) == 5 and cells[2] in ('Y', 'N'):
                fields[cells[0]] = cells
        documented[blocks[i]] = fields
    # The frozen core remains exactly13 tables; CR-001 adds separate tables.
    assert set(documented) == set(metadata.tables)
    assert set(documented) <= set(Base.metadata.tables)
    assert sum(map(len, documented.values())) == 203
    for name, fields in documented.items():
        table = Base.metadata.tables[name]
        assert set(fields) == set(table.c.keys())
        for column in table.c:
            spec = fields[column.name]
            actual = str(column.type.compile(dialect=sa.dialects.postgresql.dialect())).replace(' ', '')
            expected = spec[1].replace('TIMESTAMPTZ', 'TIMESTAMPWITHTIMEZONE')
            assert actual == expected
            assert column.nullable == (spec[2] == 'Y')


@pytest.mark.parametrize('values', [
    {'case_version': 0}, {'workflow_status': 'invented'}, {'closed_at': NOW},
    {'workflow_status': 'closed'}, {'workflow_status': 'resolved'},
    {'fulfillment_status': 'completed'}, {'fulfillment_note': 'premature'},
    {'policy_snapshot': []}, {'missing_information': {}}, {'ownership_status': 'admin'},
])
def test_case_checks_reject_incomplete_state(db, values):
    row = case(db)
    rejected(db, metadata.tables['complaints'].update().where(metadata.tables['complaints'].c.id == row.id).values(**values))


def test_canonical_thread_dedupe_and_alias(db):
    one, two = case(db), case(db, 'b')
    table = metadata.tables['complaints']
    db.execute(table.update().where(table.c.id == one.id).values(gmail_thread_id='thread'))
    rejected(db, table.update().where(table.c.id == two.id).values(gmail_thread_id='thread'))
    db.execute(table.update().where(table.c.id == two.id).values(gmail_thread_id='thread', canonical_case_id=one.id))
    rejected(db, table.update().where(table.c.id == one.id).values(canonical_case_id=one.id))


def test_composite_foreign_keys_prevent_cross_case_pointers(db):
    one, two = case(db), case(db, 'b')
    msg1, msg2 = message(db, one.id), message(db, two.id)
    dec1, dec2 = decision(db, one.id), decision(db, two.id)
    r1, r2 = reply(db, one.id, dec1, msg1), reply(db, two.id, dec2, msg2)
    cases, replies, runs = (metadata.tables[n] for n in ('complaints', 'case_replies', 'text_analysis_runs'))
    rejected(db, cases.update().where(cases.c.id == one.id).values(current_decision_id=dec2))
    rejected(db, replies.update().where(replies.c.id == r1).values(decision_id=dec2))
    rejected(db, replies.update().where(replies.c.id == r1).values(in_reply_to_message_id=msg2))
    rejected(db, replies.update().where(replies.c.id == r1).values(status='sent', sent_message_id=msg2, gmail_sent_message_id='sent', sent_at=NOW))
    rejected(db, runs.insert().values(complaint_id=one.id, message_id=msg2, provider='test', basis_case_version=1, input_hash='a'*64))
    run = uuid4()
    db.execute(runs.insert().values(id=run, complaint_id=two.id, message_id=msg2, provider='test', basis_case_version=1, input_hash='a'*64))
    rejected(db, cases.update().where(cases.c.id == one.id).values(latest_text_analysis_id=run))
    operations = metadata.tables['reply_operations']
    operation = uuid4()
    db.execute(operations.insert().values(id=operation, reply_id=r2, idempotency_key=uuid4(), operation='save_draft', expected_case_version=1, expected_revision=1, request_hash='a'*64, actor='test-staff'))
    rejected(db, replies.update().where(replies.c.id == r1).values(attempt_token=operation))
    # Valid same-case deferred cycle is accepted within one transaction.
    db.execute(cases.update().where(cases.c.id == one.id).values(current_decision_id=dec1))
    db.execute(replies.update().where(replies.c.id == r2).values(attempt_token=operation))
    db.execute(sa.text('SET CONSTRAINTS ALL IMMEDIATE'))


def test_decision_and_audit_are_rolled_back_together(db):
    row = case(db)
    audit = metadata.tables['audit_events']
    with pytest.raises(IntegrityError), db.begin_nested():
        decision(db, row.id)
        db.execute(audit.insert().values(complaint_id=row.id, event_type='test', actor='test-staff'))
        decision(db, row.id)  # Duplicate basis version must roll back both.
    assert db.scalar(sa.select(sa.func.count()).select_from(audit)) == 0
    assert db.scalar(sa.select(sa.func.count()).select_from(metadata.tables['complaint_decisions'])) == 0


def test_unknown_operation_blocks_new_dispatch_and_send_requires_confirmation(db):
    row = case(db)
    rid = reply(db, row.id, decision(db, row.id), message(db, row.id))
    table = metadata.tables['reply_operations']
    values = dict(reply_id=rid, idempotency_key=uuid4(), operation='send',
                  expected_case_version=1, expected_revision=1, request_hash='a'*64, actor='test-staff')
    rejected(db, table.insert().values(**values))
    rejected(db, table.insert().values(**values, confirmed_at=NOW, confirmed_by='another-staff'))
    op = uuid4()
    db.execute(table.insert().values(**values, id=op, confirmed_at=NOW, confirmed_by='test-staff',
                                    status='unknown', error_code='timeout', started_at=NOW, finished_at=NOW))
    values['idempotency_key'] = uuid4()
    rejected(db, table.insert().values(**values, confirmed_at=NOW, confirmed_by='test-staff'))
    db.execute(table.update().where(table.c.id == op).values(status='succeeded', error_code=None))
    db.execute(table.insert().values(**values, confirmed_at=NOW, confirmed_by='test-staff'))


@pytest.mark.parametrize('changes', [
    {'source': 'customer'}, {'size_bytes': 0}, {'size_bytes': 5242881},
    {'width_px': 2000000000, 'height_px': 2000000000}, {'width_px': 0},
    {'object_generation': 0}, {'content_type': 'image/svg+xml'}, {'sha256': 'invalid'},
    {'evidence_kind': 'customer'},
])
def test_asset_constraints(db, changes):
    order = db.scalar(sa.select(Order.id).limit(1))
    values = dict(order_id=order, source='order', evidence_kind='packing', bucket_name='test-private',
                  object_key=str(uuid4()), object_generation=1, content_type='image/png',
                  size_bytes=100, width_px=10, height_px=10, sha256='a'*64)
    values.update(changes)
    rejected(db, metadata.tables['evidence_assets'].insert().values(**values))


def test_text_and_evidence_attempts_keep_failed_stale_and_restrict_active(db):
    row = case(db)
    msg = message(db, row.id)
    table = metadata.tables['text_analysis_runs']
    values = dict(complaint_id=row.id, message_id=msg, basis_case_version=1, provider='test', input_hash='a'*64, started_at=NOW)
    rid = uuid4()
    db.execute(table.insert().values(**values, id=rid))
    rejected(db, table.insert().values(**values))
    rejected(db, table.update().where(table.c.id == rid).values(status='completed', finished_at=NOW))
    db.execute(table.update().where(table.c.id == rid).values(status='failed', finished_at=NOW, error_code='provider_timeout'))
    db.execute(table.insert().values(**values, status='stale', output={'summary': 'raw'}, finished_at=NOW))
    evidence = metadata.tables['evidence_analyses']
    ev = dict(complaint_id=row.id, basis_case_version=1, mode='single_side', asset_ids=[str(uuid4())], created_at=NOW)
    rejected(db, evidence.insert().values(**ev, status='completed', completed_at=NOW, consistency='consistent'))
    db.execute(evidence.insert().values(**ev))
    rejected(db, evidence.insert().values(**ev))


def test_session_hash_expiry_intake_resolution_and_fulfillment(db):
    sessions = metadata.tables['staff_sessions']
    values = dict(token_hash='a'*64, csrf_hash='b'*64, staff_id='test-staff', created_at=NOW)
    rejected(db, sessions.insert().values(**values, expires_at=NOW))
    db.execute(sessions.insert().values(**values, expires_at=NOW + timedelta(hours=8)))
    failures = metadata.tables['gmail_intake_failures']
    values = dict(gmail_message_id='unparsed', error_code='malformed_email', first_seen_at=NOW, last_attempt_at=NOW)
    db.execute(failures.insert().values(**values))
    rejected(db, failures.update().values(status='ignored', resolved_at=NOW, resolved_by='test-staff'))
    db.execute(failures.update().values(status='ignored', resolved_at=NOW, resolved_by='test-staff', resolution_note='Cannot parse'))
    row = case(db)
    cases = metadata.tables['complaints']
    db.execute(cases.update().where(cases.c.id == row.id).values(
        workflow_status='closed', resolved_at=NOW, closed_at=NOW, closed_by='test-staff', close_note='Completed',
        fulfillment_status='completed', fulfillment_completed_at=NOW, fulfillment_completed_by='test-staff', fulfillment_note='Done outside app'))
    db.execute(cases.update().where(cases.c.id == row.id).values(
        workflow_status='needs_review', closed_at=None, closed_by=None, close_note=None, resolved_at=None))


@pytest.fixture
def migration_database():
    # CREATE/DROP only a UUID-named database owned by this fixture. Never drop
    # application tables or touch the existing volume; all engines are disposed.
    url = sa.engine.make_url(__import__('os').environ.get('TEST_DATABASE_URL', settings.database_url))
    name = 'test_claimpilot_' + uuid4().hex
    admin = sa.create_engine(url, isolation_level='AUTOCOMMIT')
    with admin.connect() as connection:
        connection.execute(sa.text(f'CREATE DATABASE "{name}"'))
    engine = sa.create_engine(url.set(database=name))
    try:
        yield engine
    finally:
        engine.dispose()
        with admin.connect() as connection:
            connection.execute(sa.text(f'DROP DATABASE "{name}"'))
        admin.dispose()


def test_new_and_legacy_migrations_preserve_data_and_repeat(migration_database):
    engine = migration_database
    cfg = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))
    with engine.connect() as conn:
        cfg.attributes['connection'] = conn
        command.upgrade(cfg, '0004')
        old = sa.MetaData()
        cases = sa.Table('complaints', old, autoload_with=conn)
        for number, state in enumerate([True, False, None], start=1):
            conn.execute(cases.insert().values(
                gmail_message_id=f'legacy-{number}', sender_email='synthetic@example.test',
                email_subject='Original', email_body='Original body', received_at=NOW, is_complaint=state,
                missing_information=[], verification_status='not_checked', case_status='processed' if state is not None else 'processing_failed',
                complaint_type='other', requested_action='other', priority='low', ai_summary='Existing analysis'))
        before = conn.execute(sa.select(cases).order_by(cases.c.id)).all()
        conn.commit()
        command.upgrade(cfg, 'head')
        assert conn.execute(sa.select(cases).order_by(cases.c.id)).all() == before
        conn.commit()
        command.upgrade(cfg, 'head')
        command.check(cfg)
        assert backfill(conn) == 0
        messages = metadata.tables['case_messages']
        runs = metadata.tables['text_analysis_runs']
        assert conn.scalar(sa.select(sa.func.count()).select_from(messages)) == 3
        assert conn.scalar(sa.select(sa.func.count()).select_from(runs)) == 2
        assert conn.scalar(sa.select(sa.func.count()).select_from(metadata.tables['complaint_decisions'])) == 0
        assert conn.scalar(sa.select(sa.func.count()).select_from(metadata.tables['case_replies'])) == 0
        assert conn.scalar(sa.select(messages.c.id).where(messages.c.gmail_message_id == 'legacy-1')) == uuid5(NAMESPACE_URL, 'claimpilot:legacy-message:legacy-1')
        conn.commit()
        tables = set(sa.inspect(conn).get_table_names()) - {'alembic_version'}
        assert tables == set(Base.metadata.tables)
        assert sum(len(sa.inspect(conn).get_columns(t)) for t in metadata.tables) == 203
        # Legacy SERIAL sequence is still usable and new server defaults allow
        # the unchanged intake path to insert without supplying target fields.
        assert conn.scalar(metadata.tables['complaints'].insert().values(
            gmail_message_id='after-baseline', sender_email='synthetic@example.test',
            email_subject='After', email_body='Synthetic body', received_at=NOW,
        ).returning(metadata.tables['complaints'].c.id)) == 4
        conn.commit()


def test_empty_database_upgrade_has_no_schema_drift(migration_database):
    cfg = Config(str(Path(__file__).resolve().parents[1] / 'alembic.ini'))
    with migration_database.connect() as conn:
        cfg.attributes['connection'] = conn
        command.upgrade(cfg, 'head')
        command.check(cfg)
        assert conn.scalar(sa.select(sa.func.count()).select_from(metadata.tables['integration_state'])) == 1
