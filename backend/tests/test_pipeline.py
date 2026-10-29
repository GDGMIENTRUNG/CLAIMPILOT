import base64
from datetime import datetime, timezone
from email.message import EmailMessage
from unittest.mock import Mock
import pytest
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.models import Complaint, Order
from app.schemas import Analysis
from app.services.errors import IntegrationError
from app.services.gemini import validate_analysis, GeminiService
from app.services.gmail import parse_message, GmailService
from app.services.policy import assess
from app.services.sync import synchronize, sync_lock
from scripts.seed_data import seed


def analysis(order_id='DH001', **kw):
    return Analysis(complaint_type='late_delivery', order_id=order_id, requested_action=kw.get('requested_action','shipping_fee_refund'), summary='Customer reports late delivery.', missing_information=[], priority='medium')

def email(message_id='message-1', sender='dh001@example.com'):
    return dict(gmail_message_id=message_id, sender_email=sender, email_subject='Late delivery', email_body='My DH001 order was late. Please refund shipping.', received_at=datetime.now(timezone.utc))

def services(ids=None):
    gmail = Mock()
    gmail.list_ids.return_value = ['message-1'] if ids is None else ids
    gmail.get_message.side_effect = lambda ident: email(ident)
    gemini = Mock()
    gemini.analyze.return_value = analysis()
    return gmail, gemini

@pytest.mark.parametrize('order_id,verification,result', [
    ('DH001','delivered','eligible_for_review'), ('DH002','delivered','not_eligible'),
    ('DH003','not_delivered','insufficient_information'), ('UNKNOWN','order_not_found','order_not_found'),
    (None,'missing_order_id','insufficient_information'),
])
def test_policy(db, order_id, verification, result):
    sender = f'{order_id.lower()}@example.com' if order_id else 'nobody@example.com'
    order, actual_verification, matches, actual_result, reason = assess(db, analysis(order_id), sender)
    assert actual_verification == verification
    assert actual_result == result
    assert reason


def test_sender_mismatch(db):
    result = assess(db, analysis(), 'different@example.com')
    assert result[2] is False
    assert result[3] == 'insufficient_information'


def test_missing_delivery_data(db):
    order = db.scalar(select(Order).where(Order.order_id == 'DH001'))
    order.expected_delivery_date = None
    db.flush()
    result = assess(db, analysis(), 'dh001@example.com')
    assert result[1] == 'insufficient_data'


def test_unsupported_action(db):
    assert assess(db, analysis(requested_action='replacement'), 'dh001@example.com')[3] == 'insufficient_information'


def test_seed_repeatable(db):
    seed(db)
    assert db.scalar(select(func.count()).select_from(Order)) == 3


def test_sync_and_duplicate(db):
    gmail, gemini = services()
    assert synchronize(db,gmail,gemini).successful == 1
    record = db.scalar(select(Complaint))
    assert record.policy_result == 'eligible_for_review'
    assert record.verified_order.order_id == 'DH001'
    assert record.case_status == 'pending_review'
    assert synchronize(db,gmail,gemini).skipped == 1
    assert gemini.analyze.call_count == 1
    assert db.scalar(select(func.count()).select_from(Complaint)) == 1


def test_database_dedup_constraint(db):
    db.add(Complaint(**email()))
    db.commit()
    db.add(Complaint(**email()))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_failure_preserves_email_and_retry_outside_query(db, monkeypatch):
    monkeypatch.setattr("app.config.settings.gmail_retry_failed", True)
    gmail, gemini = services()
    gemini.analyze.side_effect = IntegrationError('invalid_ai_output')
    result = synchronize(db,gmail,gemini)
    assert result.failed == 1
    record = db.scalar(select(Complaint))
    assert record.email_body == email()['email_body']
    assert record.case_status == 'processing_failed'
    gemini.analyze.side_effect = None
    gmail.list_ids.return_value = []
    assert synchronize(db,gmail,gemini).successful == 1
    assert record.processing_error is None
    assert gmail.get_message.call_count == 1

@pytest.mark.parametrize('text', ['not json', '{}', '{"order_id":123}', '{"complaint_type":"fraud"}', 'null'])
def test_invalid_ai(text):
    with pytest.raises(IntegrationError, match='invalid_ai_output'):
        validate_analysis(text)


def test_valid_ai():
    assert validate_analysis(analysis().model_dump_json()).order_id == 'DH001'


def test_partial_sync(db):
    gmail, gemini = services(['bad','good'])
    gmail.get_message.side_effect = lambda ident: (_ for _ in ()).throw(IntegrationError('malformed_email')) if ident == 'bad' else email(ident)
    result = synchronize(db,gmail,gemini)
    assert (result.successful,result.failed) == (1,1)
    assert result.errors[0].error == 'malformed_email'


def raw_email(html_only=False):
    msg = EmailMessage()
    msg['From'] = 'Test Customer <dh001@example.com>'
    msg['Subject'] = 'Đơn hàng đến muộn'
    if not html_only:
        msg.set_content('Plain text ✓')
        msg.add_alternative('<p>HTML fallback</p>', subtype='html')
    else:
        msg.set_content('<p>Hello ✓</p><script>alert(1)</script><style>hidden</style>', subtype='html')
    msg.add_attachment(b'not a body',maintype='application',subtype='octet-stream',filename='data.bin')
    return dict(id='mime-message', internalDate='1793062800000', raw=base64.urlsafe_b64encode(msg.as_bytes()).decode().rstrip('='))


def test_nested_mime_and_unicode():
    parsed = parse_message(raw_email())
    assert 'Plain text ✓' in parsed['email_body']
    assert 'HTML fallback' not in parsed['email_body']
    assert parsed['email_subject'] == 'Đơn hàng đến muộn'
    assert parsed['received_at'].tzinfo is not None


def test_html_stripped():
    assert parse_message(raw_email(True))['email_body'] == 'Hello ✓'


def test_malformed_email():
    with pytest.raises(IntegrationError,match='malformed_email'):
        parse_message({'raw':'!!!'})


def test_stats_filters_and_detail(client, db):
    for i,status in enumerate(['pending_review','insufficient_information','processed','processing_failed']):
        db.add(Complaint(**email(str(i)),case_status=status,complaint_type='late_delivery'))
    db.commit()
    assert client.get('/api/dashboard/stats').json() == dict(total=4,pending_review=1,insufficient_information=1,processed=1)
    response = client.get('/api/complaints?case_status=pending_review&page_size=1')
    assert response.status_code == 200
    assert response.json()['total'] == 1
    ident = response.json()['items'][0]['id']
    assert client.get(f'/api/complaints/{ident}').json()['email_body'] == email()['email_body']
    assert client.get('/api/complaints/99999').status_code == 404
    assert client.get('/api/complaints?page=0').status_code == 422
    assert client.get('/api/complaints?case_status=invalid').status_code == 422


def test_api_sync(client,monkeypatch):
    gmail,gemini = services()
    monkeypatch.setattr('app.main.GmailService',lambda: gmail)
    monkeypatch.setattr('app.main.get_ai_service',lambda: gemini)
    assert client.post('/api/gmail/sync').json()['successful'] == 1
    assert client.post('/api/gmail/sync').json()['skipped'] == 1
    item = client.get('/api/complaints').json()['items'][0]
    detail = client.get(f"/api/complaints/{item['id']}").json()
    assert detail['verified_order']['order_id'] == 'DH001'
    assert detail['ai_summary'] == 'Customer reports late delivery.'
    assert detail['policy_result'] == 'eligible_for_review'


def test_sync_lock(client):
    sync_lock.acquire()
    try:
        assert client.post('/api/gmail/sync').status_code == 409
    finally:
        sync_lock.release()


def test_missing_gmail_config(client,monkeypatch,tmp_path):
    monkeypatch.setattr('app.config.settings.gmail_token_path',str(tmp_path/'missing.json'))
    response = client.post('/api/gmail/sync')
    assert response.status_code == 503
    assert response.json()['detail'] == 'gmail_not_authorized_run_authorize_command'


def test_missing_gemini_config(monkeypatch):
    monkeypatch.setattr('app.config.settings.gemini_api_key','')
    with pytest.raises(IntegrationError,match='gemini_not_configured'):
        GeminiService().analyze('subject','body')


def test_cors(client):
    allowed = client.options('/api/gmail/sync',headers={'Origin':'http://localhost:5173','Access-Control-Request-Method':'POST'})
    assert allowed.headers['access-control-allow-origin'] == 'http://localhost:5173'
    denied = client.options('/api/gmail/sync',headers={'Origin':'https://untrusted.example','Access-Control-Request-Method':'POST'})
    assert 'access-control-allow-origin' not in denied.headers


def test_gmail_pagination_drains_saved_backlog(monkeypatch):
    service = GmailService.__new__(GmailService)
    service.client = Mock()
    messages = service.client.users.return_value.messages.return_value
    messages.list.return_value.execute.side_effect = [
        {'messages':[{'id':'saved'}],'nextPageToken':'next'},
        {'messages':[{'id':'new'}]},
    ]
    assert service.list_ids(known_ids={'saved'}) == ['saved','new']
    assert messages.list.call_count == 2
    assert messages.list.call_args.kwargs['pageToken'] == 'next'


def test_gemini_sdk_validated_response(monkeypatch):
    monkeypatch.setattr('app.config.settings.gemini_api_key','test-key-never-used-on-network')
    client = Mock()
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=False)
    client.models.generate_content.return_value.text = analysis().model_dump_json()
    factory = Mock(return_value=client)
    monkeypatch.setattr('app.services.gemini.genai.Client',factory)
    assert GeminiService().analyze('subject','actual email body').order_id == 'DH001'
    args = client.models.generate_content.call_args.kwargs
    assert 'actual email body' in args['contents']
    assert args['config'].response_json_schema == Analysis.model_json_schema()
    assert args['config'].response_schema is None
    client.models.generate_content.return_value.text = 'invalid'
    with pytest.raises(IntegrationError,match='invalid_ai_output'):
        GeminiService().analyze('subject','body')


def test_gemini_rate_limit_sanitized(monkeypatch):
    monkeypatch.setattr('app.config.settings.gemini_api_key','test-key')
    client = Mock()
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=False)
    exc = RuntimeError('sensitive provider trace')
    exc.code = 429
    client.models.generate_content.side_effect = exc
    monkeypatch.setattr('app.services.gemini.genai.Client',Mock(return_value=client))
    with pytest.raises(IntegrationError,match='gemini_rate_limited') as caught:
        GeminiService().analyze('subject','body')
    assert 'sensitive' not in str(caught.value)


def test_policy_uses_database_dates_not_ai_complaint_category(db):
    extracted = analysis().model_copy(update={'complaint_type':'refund_request'})
    assert assess(db, extracted, 'dh001@example.com')[3] == 'eligible_for_review'


def test_database_error_is_sanitized(client):
    from sqlalchemy.exc import OperationalError
    from app.main import app
    from app.database import get_db
    def broken_db():
        raise OperationalError('private connection data',{},RuntimeError('private trace'))
        yield
    app.dependency_overrides[get_db] = broken_db
    response = client.get('/api/health')
    assert response.status_code == 503
    assert 'private' not in response.text
    assert 'Database unavailable' in response.json()['detail']


@pytest.mark.parametrize('status,expected', [(400,'gemini_request_invalid'),(401,'gemini_api_key_invalid'),(403,'gemini_access_denied'),(404,'gemini_model_not_found'),(504,'gemini_timeout_retry_sync')])
def test_gemini_error_categories(monkeypatch, status, expected):
    monkeypatch.setattr('app.config.settings.gemini_api_key','test-key')
    client = Mock()
    client.__enter__ = Mock(return_value=client)
    client.__exit__ = Mock(return_value=False)
    exc = RuntimeError('private provider details')
    exc.code = status
    client.models.generate_content.side_effect = exc
    monkeypatch.setattr('app.services.gemini.genai.Client', Mock(return_value=client))
    with pytest.raises(IntegrationError, match=expected):
        GeminiService().analyze('subject','fictional body')


def test_batch_limit_includes_saved_retries(db, monkeypatch):
    monkeypatch.setattr('app.config.settings.gmail_batch_size', 2)
    monkeypatch.setattr('app.config.settings.gmail_retry_failed', True)
    db.add(Complaint(**email('saved'), case_status='processing_failed', processing_error='invalid_ai_output'))
    db.commit()
    gmail, gemini = services(['new-1','new-2','new-3'])
    result = synchronize(db, gmail, gemini)
    assert result.successful == 2
    assert result.deferred == 2
    assert gemini.analyze.call_count == 2


def test_can_disable_old_failure_retries(db, monkeypatch):
    monkeypatch.setattr('app.config.settings.gmail_retry_failed', False)
    db.add(Complaint(**email('old'), case_status='processing_failed', processing_error='invalid_ai_output'))
    db.commit()
    gmail, gemini = services(['new'])
    assert synchronize(db, gmail, gemini).successful == 1
    old = db.scalar(select(Complaint).where(Complaint.gmail_message_id == 'old'))
    assert old.case_status == 'processing_failed'
    assert gemini.analyze.call_count == 1


def test_provider_failure_stops_remaining_batch(db):
    gmail, gemini = services(['one','two','three'])
    gemini.analyze.side_effect = IntegrationError('gemini_timeout_retry_sync')
    result = synchronize(db, gmail, gemini)
    assert (result.failed, result.deferred) == (1,2)
    assert gemini.analyze.call_count == 1
    assert gmail.get_message.call_count == 1


def test_saved_email_is_processing_during_ai_call(db):
    gmail, gemini = services()
    def inspect_status(subject, body):
        record = db.scalar(select(Complaint))
        assert record.case_status == 'processing'
        assert record.processing_error is None
        return analysis()
    gemini.analyze.side_effect = inspect_status
    assert synchronize(db, gmail, gemini).successful == 1


def test_retry_saved_email_does_not_call_gmail(client, db, monkeypatch):
    record = Complaint(**email('old-outside-query'), case_status='processing_failed', processing_error='gemini_timeout_retry_sync')
    db.add(record)
    db.commit()
    gemini = Mock()
    gemini.analyze.return_value = analysis()
    monkeypatch.setattr('app.main.get_ai_service',lambda: gemini)
    monkeypatch.setattr('app.main.GmailService',Mock(side_effect=AssertionError('Gmail must not be called')))
    response = client.post(f'/api/complaints/{record.id}/analyze')
    assert response.status_code == 200
    assert response.json()['verified_order']['order_id'] == 'DH001'
    assert response.json()['policy_result'] == 'eligible_for_review'
    assert response.json()['processing_error'] is None
    assert client.post(f'/api/complaints/{record.id}/analyze').status_code == 409
    assert gemini.analyze.call_count == 1
    assert db.scalar(select(func.count()).select_from(Complaint)) == 1


def test_retry_timeout_persists_and_lock_releases(client,db,monkeypatch):
    record = Complaint(**email(),case_status='processing_failed')
    db.add(record)
    db.commit()
    gemini = Mock()
    gemini.analyze.side_effect = IntegrationError('gemini_timeout_retry_sync')
    monkeypatch.setattr('app.main.get_ai_service',lambda:gemini)
    response = client.post(f'/api/complaints/{record.id}/analyze')
    assert response.status_code == 503
    db.refresh(record)
    assert record.case_status == 'processing_failed'
    assert record.processing_error == 'gemini_timeout_retry_sync'
    assert not sync_lock.locked()
    assert client.post('/api/complaints/999999/analyze').status_code == 404


def test_retry_conflicts_with_sync(client):
    sync_lock.acquire()
    try:
        assert client.post('/api/complaints/1/analyze').status_code == 409
    finally:
        sync_lock.release()


def test_groq_outage_stops_batch(db):
    gmail, model = services(['first','second','third'])
    model.analyze.side_effect=IntegrationError('groq_rate_limited')
    result=synchronize(db,gmail,model)
    assert (result.failed,result.deferred)==(1,2)
    assert model.analyze.call_count==1
