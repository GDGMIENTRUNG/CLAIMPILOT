"""Mailbox polling and idempotent message intake. No outbound mutations here."""
import base64,time
from email import policy
from email.parser import BytesParser
from email.utils import parseaddr
from uuid import uuid4
from fastapi import APIRouter,Depends
from sqlalchemy import select,text
from sqlalchemy.orm import Session
from app.database import get_db,engine
from app.models import Complaint,CaseMessage,IntegrationState,GmailIntakeFailure
from app.security import principal,fail,now
from app.workspace import audit,reopen_fields,get_case
from app.services.gmail import GmailService,parse_message
from app.services.errors import IntegrationError
from app.assessment import analyze
from app.knowledge import config

router=APIRouter(prefix='/api',dependencies=[Depends(principal)])
SYNC_LOCK=74261401

def parse_raw(raw,mailbox):
    encoded=raw.get('raw','')
    if len(encoded)>35*1024*1024:raise IntegrationError('mime_too_large')
    data=base64.urlsafe_b64decode(encoded+'='*(-len(encoded)%4))
    if len(data)>25*1024*1024:raise IntegrationError('mime_too_large')
    mail=BytesParser(policy=policy.default).parsebytes(data)
    legacy=parse_message(raw)
    return dict(**legacy,gmail_thread_id=raw.get('threadId'),rfc_message_id=str(mail.get('Message-ID','')) or None,
                in_reply_to=str(mail.get('In-Reply-To','')) or None,references_header=str(mail.get('References','')) or None,
                recipient_email=parseaddr(str(mail.get('To','')))[1] or None,
                direction='outbound' if legacy['sender_email'].casefold()==mailbox.casefold() else 'inbound')

def append_message(db,p,mailbox):
    previous=db.scalar(select(CaseMessage).where(CaseMessage.gmail_message_id==p['gmail_message_id']))
    if previous:return db.get(Complaint,previous.complaint_id),False,False,False
    c=db.scalar(select(Complaint).where(Complaint.gmail_thread_id==p['gmail_thread_id'],Complaint.canonical_case_id.is_(None)).with_for_update()) if p['gmail_thread_id'] else None
    if not c:c=db.scalar(select(Complaint).where(Complaint.gmail_message_id==p['gmail_message_id']).with_for_update())
    if not c and p['direction']=='outbound':return None,False,False,False
    created=not c
    if not c:
        c=Complaint(gmail_message_id=p['gmail_message_id'],gmail_thread_id=p['gmail_thread_id'],sender_email=p['sender_email'],email_subject=p['email_subject'],email_body=p['email_body'],received_at=p['received_at'],is_complaint=None)
        db.add(c);db.flush()
    elif not c.gmail_thread_id:c.gmail_thread_id=p['gmail_thread_id']
    was_closed=c.workflow_status in ('closed','resolved')
    msg=CaseMessage(complaint_id=c.id,gmail_message_id=p['gmail_message_id'],gmail_thread_id=p['gmail_thread_id'],rfc_message_id=p['rfc_message_id'],in_reply_to=p['in_reply_to'],references_header=p['references_header'],direction=p['direction'],sender_email=p['sender_email'],recipient_email=p['recipient_email'] or (mailbox if p['direction']=='inbound' else c.sender_email),subject=p['email_subject'],body=p['email_body'],occurred_at=p['received_at'],processing_status='completed' if p['direction']=='outbound' else 'pending')
    db.add(msg)
    if p['direction']=='inbound':
        if not created:c.case_version+=1
        reopen_fields(c);c.processing_status='pending';c.current_decision_id=None
        # A previously informational thread can later contain a complaint.
        # Preserve original classification in history; classify the new message.
        if c.is_complaint is False:
            c.is_complaint=None
            audit(db,c,'classification_reopened','system:sync','Email mới cần phân loại lại.',before={'is_complaint':False},after={'is_complaint':None})
        if c.sender_email.casefold()!=p['sender_email'].casefold():c.needs_manual_review=True
    audit(db,c,'message_ingested','system:sync',after={'gmail_message_id':p['gmail_message_id'],'direction':p['direction']})
    if was_closed and p['direction']=='inbound':audit(db,c,'case_reopened','system:sync','Email mới')
    failure=db.get(GmailIntakeFailure,p['gmail_message_id'])
    if failure:failure.status='resolved';failure.resolved_at=now();failure.resolved_by='system:sync'
    db.commit();return c,True,created,was_closed and p['direction']=='inbound'

def synchronize_v4(db):
    with engine.connect() as lock:
        if not lock.scalar(text('SELECT pg_try_advisory_lock(:key)'),{'key':SYNC_LOCK}):fail(409,'sync_busy')
        try:return _sync(db)
        finally:lock.execute(text('SELECT pg_advisory_unlock(:key)'),{'key':SYNC_LOCK});lock.commit()

def _sync(db):
    start=time.monotonic();state=db.get(IntegrationState,1)
    if not state:state=IntegrationState(id=1);db.add(state)
    state.last_attempt_at=now();db.commit()
    result=dict(successful=0,skipped=0,failed=0,deferred=0,errors=[],messages_added=0,cases_created=0,cases_reopened=0)
    try:
        gmail=GmailService();client=gmail.client
        mailbox=client.users().getProfile(userId='me').execute()['emailAddress']
        if state.mailbox_email and state.mailbox_email.casefold()!=mailbox.casefold():raise IntegrationError('gmail_mailbox_mismatch')
        state.mailbox_email=mailbox;db.commit()
        known=list(db.scalars(select(Complaint).where(Complaint.canonical_case_id.is_(None),Complaint.gmail_thread_id.is_not(None),Complaint.id>state.known_thread_cursor).order_by(Complaint.id).limit(20)).all())
        if not known:
            state.known_thread_cursor=0;db.commit()
            known=list(db.scalars(select(Complaint).where(Complaint.canonical_case_id.is_(None),Complaint.gmail_thread_id.is_not(None)).order_by(Complaint.id).limit(20)).all())
        pending=list(dict.fromkeys([*(state.pending_thread_ids or []),*[c.gmail_thread_id for c in known]]))
        discovery=client.users().messages().list(userId='me',q=__import__('app.config',fromlist=['settings']).settings.gmail_query,maxResults=20,pageToken=state.discovery_page_token).execute()
        ids=[m['id'] for m in discovery.get('messages',[])];state.discovery_page_token=discovery.get('nextPageToken')
        retry=list(db.scalars(select(GmailIntakeFailure.gmail_message_id).where(GmailIntakeFailure.status=='pending').limit(5)).all())
        ids=list(dict.fromkeys(retry+ids))
        for thread in pending[:20]:
            data=client.users().threads().get(userId='me',id=thread,format='metadata',metadataHeaders=['From']).execute()
            ids+= [m['id'] for m in data.get('messages',[])]
        state.pending_thread_ids=pending[20:]
        if known:state.known_thread_cursor=known[-1].id
        db.commit();attempted=0
        unique=list(dict.fromkeys(ids))
        for mid in unique:
            if db.scalar(select(CaseMessage.id).where(CaseMessage.gmail_message_id==mid)):
                result['skipped']+=1;continue
            if attempted>=5 or time.monotonic()-start>=240:
                result['deferred']+=1
                # A durable technical retry record tracks known message IDs.
                f=db.get(GmailIntakeFailure,mid)
                if not f:db.add(GmailIntakeFailure(gmail_message_id=mid,error_code='deferred_budget'))
                db.commit();continue
            attempted+=1
            try:
                raw=client.users().messages().get(userId='me',id=mid,format='raw').execute()
                p=parse_raw(raw,mailbox);c,added,created,reopened=append_message(db,p,mailbox)
                result['messages_added']+=int(added);result['cases_created']+=int(created);result['cases_reopened']+=int(reopened)
                if c and added and p['direction']=='inbound':
                    from app.evidence import ingest
                    saved=db.scalar(select(CaseMessage).where(CaseMessage.gmail_message_id==mid))
                    try:ingest(db,saved.id,base64.urlsafe_b64decode(raw['raw']+'='*(-len(raw['raw'])%4)))
                    except Exception:
                        db.rollback();audit(db,c,'evidence_ingestion_failed','system:sync','Không thể lưu ảnh; email gốc vẫn giữ.');db.commit()
                if c and added and p['direction']=='inbound':
                    if config(db,False):
                        run=analyze(db,c,c.case_version)
                        if run.status=='completed':result['successful']+=1
                        else:result['failed']+=1
                    else:
                        c.processing_status='failed';c.processing_error='config_unavailable';db.commit();result['failed']+=1
            except Exception as exc:
                db.rollback();code=exc.code if isinstance(exc,IntegrationError) else 'gmail_fetch_or_parse_failed'
                # Only pre-persistence failures belong in intake_failures.
                if not db.scalar(select(CaseMessage.id).where(CaseMessage.gmail_message_id==mid)):
                    f=db.get(GmailIntakeFailure,mid)
                    if not f:f=GmailIntakeFailure(gmail_message_id=mid,error_code=code);db.add(f)
                    else:f.attempt_count+=1;f.last_attempt_at=now();f.error_code=code
                    db.commit()
                result['failed']+=1;result['errors'].append({'message_id':mid,'error':code})
        state=db.get(IntegrationState,1);state.last_error_code=None if not result['failed'] else 'batch_has_failures'
        if not result['failed']:state.last_success_at=now()
        state.deferred_count=result['deferred']+len(state.pending_thread_ids or [])
        state.last_duration_ms=int((time.monotonic()-start)*1000);state.last_sync_summary={k:v for k,v in result.items() if k!='errors'};db.commit()
        return result
    except Exception as exc:
        db.rollback();state=db.get(IntegrationState,1);code=exc.code if isinstance(exc,IntegrationError) else 'gmail_sync_failed'
        state.last_error_code=code;state.last_duration_ms=int((time.monotonic()-start)*1000);db.commit();fail(503,code)

@router.post('/gmail/sync')
def sync(db:Session=Depends(get_db)):return synchronize_v4(db)
