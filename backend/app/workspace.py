"""Read projections and shared case transactions, independent of provider calls."""
from contextlib import contextmanager
from decimal import Decimal
from datetime import date,datetime
from uuid import UUID
from sqlalchemy import select
from app.models import (Complaint,CaseMessage,ComplaintDecision,CaseReply,AuditEvent,Order,
                        ReplyOperation,AgentRun,AgentStep,ReplyCheck)
from app.security import fail,now

def encode(value):
    if isinstance(value,(datetime,date)):return value.isoformat()
    if isinstance(value,(UUID,Decimal)):return str(value)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encode(v) for v in value]
    return value

def row(obj):
    return encode({c.key:getattr(obj,c.key) for c in obj.__table__.columns})

def get_case(db,case_id,lock=False):
    c=db.get(Complaint,case_id)
    if c and c.canonical_case_id:c=db.get(Complaint,c.canonical_case_id)
    if not c or c.is_complaint is False:fail(404,'complaint_not_found')
    if lock:c=db.scalar(select(Complaint).where(Complaint.id==c.id).with_for_update().execution_options(populate_existing=True))
    return c

def version(c,expected):
    if c.case_version!=expected:fail(409,'stale_version')

def audit(db,c,event,actor,note='',before=None,after=None):
    db.add(AuditEvent(complaint_id=c.id,event_type=event,actor=actor,note=note,before_data=encode(before or {}),after_data=encode(after or {})))

def busy(db,c):
    unsettled=db.scalar(select(ReplyOperation.id).join(CaseReply,ReplyOperation.reply_id==CaseReply.id).where(CaseReply.complaint_id==c.id,ReplyOperation.status.in_(['in_progress','unknown'])))
    if unsettled:fail(409,'reply_busy_or_unknown')

@contextmanager
def mutate(db,case_id,expected,actor,note,event,allow_closed=False):
    try:
        c=get_case(db,case_id,True);version(c,expected);busy(db,c)
        if c.workflow_status=='closed' and not allow_closed:fail(409,'invalid_case_state')
        before={'case_version':c.case_version,'workflow_status':c.workflow_status,'current_decision_id':c.current_decision_id}
        yield c
        c.case_version+=1;c.updated_at=now()
        audit(db,c,event,actor,note,before,{'case_version':c.case_version,'workflow_status':c.workflow_status,'current_decision_id':c.current_decision_id})
        db.commit()
    except Exception:
        db.rollback();raise

def reopen_fields(c):
    c.workflow_status='needs_review';c.closed_at=None;c.closed_by=None;c.close_note=None;c.resolved_at=None

def public_reply(r,c):
    d=row(r)
    for k in ('attempt_token','outbound_rfc_message_id'):d.pop(k,None)
    d['is_stale']=r.status!='sent' and (r.basis_case_version!=c.case_version or r.decision_id!=c.current_decision_id)
    d['has_draft']=bool(r.gmail_draft_id)
    return d

def summary(db,c):
    d=row(c)
    decision=db.get(ComplaintDecision,c.current_decision_id) if c.current_decision_id else None
    d['decision_status']={'approve':'approved','reject':'rejected','request_information':'more_information_requested'}.get(decision.action if decision else '', 'undecided')
    last=db.scalar(select(CaseMessage).where(CaseMessage.complaint_id==c.id).order_by(CaseMessage.occurred_at.desc(),CaseMessage.id.desc()).limit(1))
    reply=db.scalar(select(CaseReply).where(CaseReply.decision_id==c.current_decision_id)) if c.current_decision_id else None
    snap = c.policy_snapshot or {}
    d.update(
        last_message_at=encode(last.occurred_at if last else c.received_at),
        reply_status=reply.status if reply else None,
        severity=snap.get('severity', 'low' if c.is_complaint else 'low'),
        escalation_reasons=snap.get('escalation_reasons', []),
        taken_over_by=snap.get('taken_over_by'),
        requires_immediate_takeover=snap.get('requires_immediate_takeover', False),
        case_report=snap.get('case_report')
    )
    return d

def run_json(db,r):
    d=row(r);steps=db.scalars(select(AgentStep).where(AgentStep.run_id==r.id).order_by(AgentStep.created_at,AgentStep.id)).all()
    d['steps']=[]
    for s in steps:
        v=row(s);v.pop('input_snapshot',None);d['steps'].append(v)
    return d

def detail(db,c):
    d=summary(db,c)
    order=db.get(Order,c.verified_order_id) if c.verified_order_id else None
    d['verified_order']=row(order) if order else None
    for field,model,timefield in [('messages',CaseMessage,'occurred_at'),('decisions',ComplaintDecision,'created_at'),('audit_events',AuditEvent,'created_at')]:
        d[field]=[row(o) for o in db.scalars(select(model).where(model.complaint_id==c.id).order_by(getattr(model,timefield),model.id)).all()]
    d['replies']=[public_reply(o,c) for o in db.scalars(select(CaseReply).where(CaseReply.complaint_id==c.id).order_by(CaseReply.created_at,CaseReply.id)).all()]
    run=db.scalar(select(AgentRun).where(AgentRun.complaint_id==c.id).order_by(AgentRun.created_at.desc()).limit(1))
    d['agent_run']=run_json(db,run) if run else None
    d['fulfillment_details']=dict(completed_at=encode(c.fulfillment_completed_at),completed_by=c.fulfillment_completed_by,reference=c.fulfillment_reference,note=c.fulfillment_note)
    return d
