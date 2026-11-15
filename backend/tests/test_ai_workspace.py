"""Real PostgreSQL + authenticated API acceptance for the local AI-first app.

No test calls a live AI provider or Gmail. Dispatch faults use explicit doubles.
"""
import json
from datetime import timedelta
from pathlib import Path
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select,func,text
from app.main import app
from app.database import get_db
from app import security
from app.config import settings
from app.models import (Complaint,Order,CaseMessage,KnowledgeRevision,AgentRun,AgentStep,IntegrationState,ReplyOperation,AuditEvent,CaseReply,SettingsVersion)
from app.knowledge import retrieve
from app.workspace import get_case
from app.resolution import SendInput,dispatch

ORIGIN='http://localhost:8080'
@pytest.fixture
def web(db,tmp_path,monkeypatch):
    password='synthetic-test-password'
    file=tmp_path/'staff.json'
    file.write_text(json.dumps({'username':'tester','password_hash':security.hasher.hash(password),'preview_key':'test-only-preview-secret'}))
    monkeypatch.setattr(settings,'local_credentials_path',str(file));monkeypatch.setattr(settings,'public_base_url',ORIGIN)
    monkeypatch.setattr(settings,'local_demo_login',False)
    security.attempts.clear()
    app.dependency_overrides[get_db]=lambda:db
    with TestClient(app) as client:
        client.headers['Origin']=ORIGIN
        login=client.post('/api/auth/login',json={'username':'tester','password':password})
        assert login.status_code==200,login.text
        client.headers['X-CSRF-Token']=login.json()['csrf_token']
        yield client
    app.dependency_overrides.clear()

def setup_business(web):
    r=web.patch('/api/settings/business',json={'expected_revision':0,'display_name':'Synthetic Shop','language':'vi','tone':'friendly','note':'Synthetic setup'})
    assert r.status_code==200,r.text
    return r.json()

def article(web,publish=True):
    r=web.post('/api/knowledge',json={'title':'Giao hàng trễ và hoàn phí','body':'Giao hàng trễ: nhân viên kiểm tra ngày giao và xem xét hoàn phí vận chuyển. Không tự động hoàn tiền.','topic':'late_delivery','source_label':'Synthetic policy'})
    assert r.status_code==201,r.text
    v=r.json()['revision'];base=f"/api/knowledge/{v['article_id']}/revisions/{v['id']}"
    if publish:
        r=web.post(base+'/submit',json={'expected_updated_at':v['updated_at']});assert r.status_code==200,r.text;v=r.json()
        r=web.post(base+'/approve',json={'expected_updated_at':v['updated_at'],'note':'Synthetic staff approval'});assert r.status_code==200,r.text;v=r.json()
    return v,base

def case(db):
    t=security.now();o=Order(order_id='SYNTHETIC001',customer_email='customer@example.test',order_status='Delivered',expected_delivery_date=t.date()-timedelta(days=4),actual_delivery_date=t.date()-timedelta(days=2),shipping_fee=40000,total_amount=400000)
    db.add(o);db.flush()
    c=Complaint(gmail_message_id=str(uuid4()),gmail_thread_id=str(uuid4()),sender_email='customer@example.test',email_subject='Giao hàng trễ',email_body='Đơn SYNTHETIC001 giao trễ. Xin kiểm tra giúp.',received_at=t,is_complaint=True,order_id=o.order_id,verified_order_id=o.id,ownership_status='email_matched',complaint_type='late_delivery',requested_action='shipping_fee_refund',processing_status='completed')
    db.add(c);db.flush();db.add(CaseMessage(complaint_id=c.id,gmail_message_id=c.gmail_message_id,gmail_thread_id=c.gmail_thread_id,direction='inbound',sender_email=c.sender_email,subject=c.email_subject,body=c.email_body,occurred_at=t,processing_status='completed'));db.commit();return c

def reply(web,db,body='Xin chào, chúng tôi đã tiếp nhận yêu cầu và đang kiểm tra thông tin. Cảm ơn bạn.'):
    setup_business(web);c=case(db)
    d=web.post(f'/api/complaints/{c.id}/decisions',json={'expected_case_version':c.case_version,'action':'request_information','resolution':'request_information','note':'Synthetic review','missing_fields':['Thông tin bổ sung']})
    assert d.status_code==201,d.text
    r=web.post(f'/api/complaints/{c.id}/replies/prepare',json={'expected_case_version':d.json()['case_version'],'decision_id':d.json()['decision']['id'],'mode':'manual'})
    assert r.status_code==200,r.text
    rid=r.json()['reply']['id'];base=f'/api/complaints/{c.id}/replies/{rid}'
    r=web.patch(base,json={'expected_reply_revision':1,'body':body});assert r.status_code==200,r.text
    p=web.post(base+'/preview',json={'expected_case_version':d.json()['case_version'],'expected_revision':2})
    assert p.status_code==200,p.text
    return c,base,p.json()

def test_auth_and_csrf_real_application(web):
    with TestClient(app) as anonymous:
        assert anonymous.get('/api/health').status_code==200
        for route in ('/api/complaints','/api/knowledge','/api/settings/business','/api/orders'):
            assert anonymous.get(route).status_code==401
    token=web.headers.pop('X-CSRF-Token')
    assert web.patch('/api/settings/business',json={'expected_revision':0,'note':'test'}).status_code==403
    web.headers['X-CSRF-Token']=token
    assert web.post('/api/auth/logout').status_code==204
    assert web.get('/api/auth/me').status_code==401

def test_login_rate_limit_untrusted_origin(web):
    with TestClient(app) as client:
        assert client.post('/api/auth/login',headers={'Origin':'https://evil.test'},json={'username':'tester','password':'wrong'}).status_code==403
        for _ in range(5):assert client.post('/api/auth/login',headers={'Origin':ORIGIN},json={'username':'tester','password':'wrong'}).status_code==401
        assert client.post('/api/auth/login',headers={'Origin':ORIGIN},json={'username':'tester','password':'wrong'}).status_code==429

def test_local_demo_accepts_arbitrary_credentials_keeps_session_csrf(web,monkeypatch):
    monkeypatch.setattr(settings,'local_demo_login',True)
    monkeypatch.delenv('K_SERVICE',raising=False);monkeypatch.delenv('CLOUD_RUN_JOB',raising=False)
    with TestClient(app,base_url=ORIGIN,client=('127.0.0.1',50100)) as client:
        client.headers['Origin']=ORIGIN
        assert client.get('/api/auth/config').json()=={'demo_login':True}
        assert client.get('/api/orders').status_code==401
        result=client.post('/api/auth/login',json={'username':'Nhân viên demo','password':'anything-123'})
        assert result.status_code==200,result.text
        assert result.json()['username']=='Nhân viên demo' and result.json()['csrf_token']
        assert 'httponly' in result.headers['set-cookie'].lower()
        assert client.get('/api/auth/me').json()['username']=='Nhân viên demo'
        assert client.get('/api/orders').status_code==200
        assert client.post('/api/auth/logout').status_code==403
        client.headers['X-CSRF-Token']=result.json()['csrf_token']
        assert client.post('/api/auth/logout').status_code==204
        assert client.get('/api/auth/me').status_code==401

@pytest.mark.parametrize('variant',['disabled','cloud','public_url','remote_client','forwarded','cloudflare'])
def test_demo_login_is_confined_to_explicit_local_mode(web,monkeypatch,variant):
    monkeypatch.setattr(settings,'local_demo_login',variant!='disabled')
    monkeypatch.delenv('K_SERVICE',raising=False);monkeypatch.delenv('CLOUD_RUN_JOB',raising=False)
    if variant=='cloud':monkeypatch.setenv('K_SERVICE','synthetic-cloud-service')
    origin='https://workspace.example.test' if variant=='public_url' else ORIGIN
    monkeypatch.setattr(settings,'public_base_url',origin)
    host='203.0.113.25' if variant=='remote_client' else '127.0.0.1'
    with TestClient(app,base_url=origin,client=(host,50100)) as client:
        client.headers['Origin']=origin
        if variant=='forwarded':client.headers['X-Forwarded-For']='127.0.0.1'
        if variant=='cloudflare':client.headers['CF-Ray']='synthetic-proxy-request'
        assert client.get('/api/auth/config').json()=={'demo_login':False}
        assert client.post('/api/auth/login',json={'username':'arbitrary','password':'arbitrary'}).status_code==401

def test_demo_login_still_rejects_untrusted_origin(web,monkeypatch):
    monkeypatch.setattr(settings,'local_demo_login',True)
    with TestClient(app,base_url=ORIGIN,client=('127.0.0.1',50100)) as client:
        r=client.post('/api/auth/login',headers={'Origin':'https://evil.example.test'},json={'username':'demo','password':'demo'})
        assert r.status_code==403

def test_settings_revision_validation_and_guardrails(web,db):
    cfg=setup_business(web)
    assert web.patch('/api/settings/business',json={'expected_revision':0,'display_name':'Overwrite','note':'bad'}).status_code==409
    assert web.patch('/api/settings/agents',json={'expected_revision':1,'optional_roles':['safety_quality'],'review_threshold':1,'note':'bad'}).status_code==422
    r=web.patch('/api/settings/agents',json={'expected_revision':1,'optional_roles':[],'review_threshold':.8,'note':'Synthetic threshold'})
    assert r.status_code==200 and r.json()['revision']==2
    assert db.scalar(select(func.count()).select_from(SettingsVersion))==2
    assert web.get('/api/settings/business').json()['display_name']=='Synthetic Shop'

def test_knowledge_draft_publish_archive_and_sources(web,db):
    v,base=article(web,False)
    assert retrieve(db,'Giao hàng trễ')==[]
    assert web.post(base+'/approve',json={'expected_updated_at':v['updated_at']}).status_code==409
    r=web.post(base+'/submit',json={'expected_updated_at':v['updated_at']});v=r.json()
    r=web.post(base+'/approve',json={'expected_updated_at':v['updated_at']});v=r.json();assert r.status_code==200
    refs=retrieve(db,'Giao hàng trễ');assert len(refs)==1 and refs[0]['id']==v['id']
    assert web.patch(base,json={'expected_updated_at':v['updated_at'],'body':'overwrite'}).status_code==409
    hist=web.get('/api/knowledge/'+v['article_id']).json();assert len(hist['events'])==3
    r=web.post(base+'/archive',json={'expected_updated_at':v['updated_at'],'note':'Synthetic archive'});assert r.status_code==200
    assert retrieve(db,'Giao hàng trễ')==[]
    assert web.get(base).json()['body']==v['body']

def test_knowledge_new_revision_keeps_citation_history(web,db):
    v,base=article(web)
    r=web.post('/api/knowledge/'+v['article_id']+'/revisions',json={'expected_revision':1,'title':'Second','body':'Second body','topic':'Policy','source_label':'Test'})
    assert r.status_code==201 and r.json()['revision']['revision']==2
    assert web.get(base).json()['body']==v['body']
    assert retrieve(db,'Giao hàng trễ')[0]['version']=='1'

def test_manual_decision_composer_preview_without_gmail(web,db):
    c,base,p=reply(web,db)
    assert p['quality_check']['status']=='passed' and p['preview_token']
    assert p['check']==p['quality_check']
    assert db.scalar(select(func.count()).select_from(ReplyOperation))==0
    assert len(web.get(f'/api/complaints/{c.id}').json()['messages'])==1

def test_unsafe_claim_blocked_and_body_preserved(web,db):
    c,base,p=reply(web,db,'Chúng tôi đã hoàn tiền cho bạn.')
    assert p['quality_check']['status']=='blocked' and p['preview_token'] is None
    assert web.get(base).json()['reply']['body']=='Chúng tôi đã hoàn tiền cho bạn.'

def test_edit_invalidates_preview_no_gmail_call(web,db):
    c,base,p=reply(web,db)
    r=web.patch(base,json={'expected_reply_revision':2,'body':'Nội dung đã thay đổi, xin bổ sung thông tin.'});assert r.status_code==200
    r=web.post(base+'/send',json={'expected_case_version':c.case_version,'expected_reply_revision':3,'confirmed':True,'preview_token':p['preview_token'],'idempotency_key':str(uuid4())})
    assert r.status_code==409 and db.scalar(select(func.count()).select_from(ReplyOperation))==0

def test_configuration_change_invalidates_preview(web,db):
    c,base,p=reply(web,db)
    assert web.patch('/api/settings/business',json={'expected_revision':1,'tone':'formal','note':'New tone'}).status_code==200
    r=web.post(base+'/send',json={'expected_case_version':c.case_version,'expected_reply_revision':2,'confirmed':True,'preview_token':p['preview_token'],'idempotency_key':str(uuid4())})
    assert r.status_code==409 and db.scalar(select(func.count()).select_from(ReplyOperation))==0

def test_source_archive_invalidates_preview(web,db):
    v,kbase=article(web)
    c,base,p=reply(web,db)
    assert p['sources']
    assert web.post(kbase+'/archive',json={'expected_updated_at':v['updated_at'],'note':'Archive source'}).status_code==200
    r=web.post(base+'/send',json={'expected_case_version':c.case_version,'expected_reply_revision':2,'confirmed':True,'preview_token':p['preview_token'],'idempotency_key':str(uuid4())})
    assert r.status_code==409 and db.scalar(select(func.count()).select_from(ReplyOperation))==0

def test_gmail_write_disabled_explicit_failure(web,db,monkeypatch):
    monkeypatch.setattr(settings,'enable_gmail_write',False)
    c,base,p=reply(web,db)
    r=web.post(base+'/send',json={'expected_case_version':c.case_version,'expected_reply_revision':2,'confirmed':True,'preview_token':p['preview_token'],'idempotency_key':str(uuid4())})
    assert r.status_code==503 and r.json()['code']=='gmail_write_not_enabled'
    assert db.scalar(select(ReplyOperation)).status=='failed'

def test_real_database_reserved_send_and_replay_with_fake_gmail(web,db):
    c,base,p=reply(web,db)
    db.add(IntegrationState(id=1,mailbox_email='staff@example.test'));db.commit()
    class Writer:
        calls=0
        def dispatch(self,c,r,operation,snapshot):self.calls+=1;return {'id':'synthetic-sent','threadId':c.gmail_thread_id}
    writer=Writer();rid=UUID_from_path=__import__('uuid').UUID(base.rsplit('/',1)[1])
    data=SendInput(expected_case_version=c.case_version,expected_reply_revision=2,idempotency_key=uuid4(),confirmed=True,preview_token=p['preview_token'])
    one=dispatch(db,c.id,rid,data,'tester','send',writer);two=dispatch(db,c.id,rid,data,'tester','send',writer)
    assert writer.calls==1 and one['reply']['status']==two['reply']['status']=='sent'
    assert db.scalar(select(func.count()).select_from(CaseMessage).where(CaseMessage.direction=='outbound'))==1

def test_provider_failure_keeps_message_and_records_attempt(web,db,monkeypatch):
    setup_business(web);c=case(db)
    from app import assessment
    from app.services.errors import IntegrationError
    class Broken:
        def analyze(self,*args):raise IntegrationError('synthetic_provider_timeout')
    monkeypatch.setattr(assessment,'get_ai_service',lambda:Broken())
    r=web.post(f'/api/complaints/{c.id}/agent-runs',json={'expected_case_version':1})
    assert r.status_code==202,r.text
    assert r.json()['run']['status']=='review_required'
    assert db.scalar(select(func.count()).select_from(CaseMessage))==1
    assert db.scalar(select(AgentStep).where(AgentStep.role=='intake_classification')).status=='failed'

def test_queue_filter_and_search_escaping(web,db):
    c=case(db)
    assert web.get('/api/complaints',params={'q':'SYNTHETIC001'}).json()['total']==1
    assert web.get('/api/complaints',params={'q':"%' OR 1=1 --"}).json()['total']==0
    assert web.get('/api/complaints',params={'queue':'technical'}).json()['total']==0

def test_validation_does_not_echo_password(web):
    secret='s'*300
    response=web.post('/api/auth/login',json={'username':'tester','password':secret})
    assert response.status_code==422 and secret not in response.text

def test_private_images_and_mime_validation(web,db,tmp_path,monkeypatch):
    import io
    from email.message import EmailMessage
    from PIL import Image
    from app import evidence
    from app.models import EvidenceAsset
    monkeypatch.setattr(evidence,'ROOT',tmp_path)
    c=case(db);msg=db.scalar(select(CaseMessage).where(CaseMessage.complaint_id==c.id))
    stream=io.BytesIO();Image.new('RGB',(10,10),'white').save(stream,format='PNG')
    mail=EmailMessage();mail.set_content('Synthetic evidence');mail.add_attachment(stream.getvalue(),maintype='image',subtype='png',filename='synthetic.png')
    added,errors=evidence.ingest(db,msg.id,mail.as_bytes())
    assert added==1 and not errors
    assert evidence.ingest(db,msg.id,mail.as_bytes())[0]==0
    asset=db.scalar(select(EvidenceAsset))
    assert asset.width_px==asset.height_px==10
    response=web.get(f'/api/evidence/{asset.id}/content')
    assert response.status_code==200 and response.headers['cache-control']=='private, no-store'
    with TestClient(app) as anonymous:assert anonymous.get(f'/api/evidence/{asset.id}/content').status_code==401
    with pytest.raises(ValueError):evidence.image_info(b'not an image','image/svg+xml')

def test_expired_conflicted_and_forged_sources_not_retrieved(web,db):
    from app.knowledge import valid_refs
    v,base=article(web)
    current=retrieve(db,'Giao hàng trễ');assert current
    assert not valid_refs(db,[{**current[0],'digest':'0'*64}])
    r=web.post(base+'/conflict',json={'expected_updated_at':v['updated_at'],'has_conflict':True,'note':'Contradicting evidence'})
    assert r.status_code==200 and not retrieve(db,'Giao hàng trễ')
    assert not valid_refs(db,current)

def test_ambiguous_send_blocks_replay_and_never_retries(web,db):
    c,base,p=reply(web,db)
    class TimeoutWriter:
        calls=0
        def dispatch(self,*args):self.calls+=1;raise TimeoutError('synthetic network timeout')
    writer=TimeoutWriter();rid=__import__('uuid').UUID(base.rsplit('/',1)[1])
    data=SendInput(expected_case_version=c.case_version,expected_reply_revision=2,idempotency_key=uuid4(),confirmed=True,preview_token=p['preview_token'])
    from fastapi import HTTPException
    for _ in range(2):
        with pytest.raises(HTTPException):dispatch(db,c.id,rid,data,'tester','send',writer)
    assert writer.calls==1 and db.scalar(select(ReplyOperation)).status=='unknown'

def test_scope_of_unknown_api_and_public_health(web):
    assert web.get('/api/does-not-exist').status_code==404
    assert web.get('/api/health').json()=={'status':'ok'}

def test_staff_context_review_preserves_body_requires_new_preview(web,db):
    c,base,p=reply(web,db)
    original=p['reply']['body'];old_token=p['preview_token']
    c.case_version+=1;db.commit()  # Fresh context, same staff decision.
    r=web.post(base+'/review-context',json={'expected_case_version':c.case_version,'expected_reply_revision':2,'note':'Đã đối chiếu lại quyết định và hội thoại.'})
    assert r.status_code==200,r.text
    assert r.json()['reply']['revision']==3 and r.json()['reply']['body']==original
    assert not r.json()['reply']['is_stale'] and r.json()['preview_token'] is None
    assert r.json()['quality_check']['status']=='stale'
    sent=web.post(base+'/send',json={'expected_case_version':c.case_version,'expected_reply_revision':3,'confirmed':True,'preview_token':old_token,'idempotency_key':str(uuid4())})
    assert sent.status_code==409 and db.scalar(select(func.count()).select_from(ReplyOperation))==0
    new=web.post(base+'/preview',json={'expected_case_version':c.case_version,'expected_revision':3})
    assert new.status_code==200 and new.json()['preview_token']
    assert db.scalar(select(AuditEvent).where(AuditEvent.event_type=='reply_context_reviewed')).note

def test_context_review_conflicts_do_not_change_reply(web,db):
    c,base,p=reply(web,db)
    assert web.post(base+'/review-context',json={'expected_case_version':c.case_version+1,'expected_reply_revision':2,'note':'Review'}).status_code==409
    assert web.post(base+'/review-context',json={'expected_case_version':c.case_version,'expected_reply_revision':1,'note':'Review'}).status_code==409
    d=web.post(f'/api/complaints/{c.id}/decisions',json={'expected_case_version':c.case_version,'action':'reject','resolution':'decline','note':'New staff decision'})
    assert d.status_code==201
    r=web.post(base+'/review-context',json={'expected_case_version':d.json()['case_version'],'expected_reply_revision':2,'note':'Review old reply'})
    assert r.status_code==409 and r.json()['detail']=='decision_changed'
    assert web.get(base).json()['reply']['revision']==2

def test_staff_review_refreshes_sources_with_immutable_prior_checks(web,db):
    v,kbase=article(web);c,base,p=reply(web,db)
    original_check=p['quality_check']['id'];assert p['sources'][0]['id']==v['id']
    assert web.post(kbase+'/archive',json={'expected_updated_at':v['updated_at'],'note':'Policy retired'}).status_code==200
    r=web.post(base+'/review-context',json={'expected_case_version':c.case_version,'expected_reply_revision':2,'note':'Đã đọc lại và giữ nội dung yêu cầu kiểm tra, không dựa vào chính sách cũ.'})
    assert r.status_code==200,r.text
    check=web.post(base+'/preview',json={'expected_case_version':c.case_version,'expected_revision':3}).json()
    assert check['quality_check']['status']=='passed' and check['sources']==[]
    history=web.get(base+'/checks').json()['items']
    assert next(x for x in history if x['id']==original_check)['source_refs'][0]['id']==v['id']

def test_reply_sources_bound_to_own_writer_run(web,db):
    from app.resolution import reply_writer
    c,base,p=reply(web,db)
    old=db.get(CaseReply,__import__('uuid').UUID(p['reply']['id']));first=reply_writer(db,old)
    d=web.post(f'/api/complaints/{c.id}/decisions',json={'expected_case_version':c.case_version,'action':'reject','resolution':'decline','note':'Second decision'}).json()
    r=web.post(f'/api/complaints/{c.id}/replies/prepare',json={'expected_case_version':d['case_version'],'decision_id':d['decision']['id'],'mode':'manual'})
    assert r.status_code==200,r.text
    new=db.get(CaseReply,__import__('uuid').UUID(r.json()['reply']['id']))
    assert reply_writer(db,old).run_id==first.run_id
    assert reply_writer(db,new).run_id!=first.run_id

def test_followup_reclassifies_previously_noncomplaint_thread(db):
    from app.intake import append_message
    c=case(db);c.is_complaint=False;db.commit();before=c.case_version
    p={'gmail_message_id':str(uuid4()),'gmail_thread_id':c.gmail_thread_id,'sender_email':c.sender_email,'email_subject':'Follow-up complaint','email_body':'Đơn bị giao sai, cần hỗ trợ.','received_at':security.now(),'rfc_message_id':'<synthetic-followup@example.test>','in_reply_to':None,'references_header':None,'recipient_email':'business@example.test','direction':'inbound'}
    result,added,created,_=append_message(db,p,'business@example.test')
    assert added and not created and result.id==c.id and result.is_complaint is None
    assert result.case_version==before+1 and get_case(db,c.id).processing_status=='pending'
    assert append_message(db,p,'business@example.test')[1] is False
    assert db.scalar(select(func.count()).select_from(CaseMessage).where(CaseMessage.complaint_id==c.id))==2
    assert db.scalar(select(AuditEvent).where(AuditEvent.event_type=='classification_reopened'))

@pytest.mark.parametrize('field',['valid_until','review_due_at'])
def test_kb_dates_require_timezone_and_block_expired_approval(web,field):
    payload={'title':'Synthetic expired','body':'Policy body','topic':'Test','source_label':'Test',field:'2020-01-01T00:00:00'}
    assert web.post('/api/knowledge',json=payload).status_code==422
    payload[field]+='+00:00'
    r=web.post('/api/knowledge',json=payload);assert r.status_code==201,r.text
    v=r.json()['revision'];base=f"/api/knowledge/{v['article_id']}/revisions/{v['id']}"
    v=web.post(base+'/submit',json={'expected_updated_at':v['updated_at']}).json()
    assert web.post(base+'/approve',json={'expected_updated_at':v['updated_at'],'note':'Review expired policy'}).status_code==409

def test_source_article_identity_must_match(web,db):
    from app.knowledge import valid_refs
    article(web);refs=retrieve(db,'Giao hàng trễ');assert valid_refs(db,refs)
    assert not valid_refs(db,[{**refs[0],'article_id':str(uuid4())}])

@pytest.mark.parametrize('provider_fails',[False,True])
def test_agent_completion_preserves_newer_staff_context(web,db,monkeypatch,provider_fails):
    from app import assessment
    from app.schemas import Analysis
    from app.services.errors import IntegrationError
    from app.workspace import mutate
    setup_business(web);c=case(db);basis=c.case_version
    class Delayed:
        def analyze(self,*args):
            # A real case transaction arrives while the provider is outside locks.
            with mutate(db,c.id,basis,'tester','New manual facts','manual_review') as newer:
                newer.ai_summary='Newer staff context';newer.processing_status='completed'
            if provider_fails:raise IntegrationError('synthetic_provider_timeout')
            return Analysis(is_complaint=True,complaint_type='wrong_item',order_id=None,requested_action='replacement',summary='Obsolete provider output',missing_information=[],priority='high')
    monkeypatch.setattr(assessment,'get_ai_service',lambda:Delayed())
    r=web.post(f'/api/complaints/{c.id}/agent-runs',json={'expected_case_version':basis})
    assert r.status_code==202,r.text
    assert r.json()['run']['status']=='stale'
    db.refresh(c)
    assert c.ai_summary=='Newer staff context' and c.complaint_type=='late_delivery'
    assert c.processing_status=='completed' and c.case_version==basis+1

def test_uncalibrated_confidence_cannot_pass_configured_threshold(web,db,monkeypatch):
    from app import assessment
    from app.schemas import Analysis
    setup_business(web);article(web);c=case(db)
    r=web.patch('/api/settings/agents',json={'expected_revision':1,'optional_roles':[],'review_threshold':0.9,'note':'Require confidence review'})
    assert r.status_code==200,r.text
    class Provider:
        def analyze(self,*args):
            return Analysis(is_complaint=True,complaint_type='late_delivery',order_id=c.order_id,requested_action='shipping_fee_refund',summary='Synthetic classification',missing_information=[],priority='medium')
    monkeypatch.setattr(assessment,'get_ai_service',lambda:Provider())
    r=web.post(f'/api/complaints/{c.id}/agent-runs',json={'expected_case_version':c.case_version})
    assert r.status_code==202,r.text
    run=r.json()['run']
    assert all(s['status']=='completed' for s in run['steps'] if s['role'] in run['required_roles'])
    assert run['status']=='review_required'
    classification=next(s for s in run['steps'] if s['role']=='intake_classification')
    assert classification['confidence'] is None and classification['output']['confidence_status']=='not_calibrated'
