"""ClaimPilot AI-first local application: all business routes require a session."""
from fastapi import FastAPI,Depends,Query,HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy import select,func,text,or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from app.config import settings
from app.database import get_db
from app.models import Complaint,Order,IntegrationState,GmailIntakeFailure,AgentRun,AgentStep
from app import security,knowledge,assessment,resolution,intake,evidence
from app.security import principal,fail
from app.workspace import summary,detail,get_case,row
from app.services.errors import IntegrationError

app=FastAPI(title='ClaimPilot AI-first',version='0.4.0')
app.add_middleware(CORSMiddleware,allow_origins=list({settings.frontend_origin,settings.public_base_url}),allow_credentials=True,allow_methods=['GET','POST','PATCH','OPTIONS'],allow_headers=['Content-Type','X-CSRF-Token'])
@app.exception_handler(HTTPException)
async def http_error(request,exc):return JSONResponse(status_code=exc.status_code,content={'detail':exc.detail,'code':exc.detail if isinstance(exc.detail,str) else 'request_invalid'},headers=exc.headers)
@app.exception_handler(SQLAlchemyError)
async def database_error(request,exc):return JSONResponse(status_code=409 if isinstance(exc,IntegrityError) else 503,content={'detail':'data_conflict' if isinstance(exc,IntegrityError) else 'database_unavailable','code':'data_conflict' if isinstance(exc,IntegrityError) else 'database_unavailable'})
@app.exception_handler(IntegrationError)
async def provider_error(request,exc):return JSONResponse(status_code=503,content={'detail':exc.code,'code':exc.code})
@app.exception_handler(RequestValidationError)
async def validation_error(request,exc):
    return JSONResponse(status_code=422,content={'detail':[{'loc':list(e['loc']),'msg':e['msg'],'type':e['type']} for e in exc.errors()],'code':'validation_error'})
@app.get('/api/health')
def health(db:Session=Depends(get_db)):
    db.execute(text('SELECT 1'));return {'status':'ok'}
for router in (security.router,knowledge.router,assessment.router,resolution.router,intake.router,evidence.router):app.include_router(router)

@app.get('/api/integrations/status',dependencies=[Depends(principal)])
def integrations(db:Session=Depends(get_db)):
    state=db.get(IntegrationState,1)
    return dict(gmail_configured=settings.token_path.is_file(),gemini_configured=bool(settings.gemini_api_key),ai_provider=settings.ai_provider,ai_model=settings.groq_model if settings.ai_provider=='groq' else settings.gemini_model,ai_configured=bool(settings.groq_api_key if settings.ai_provider=='groq' else settings.gemini_api_key),gmail_write_enabled=settings.enable_gmail_write,environment='local',note='Có cấu hình không đồng nghĩa đã kiểm kết nối. Không tự gửi thư.',last_attempt_at=state.last_attempt_at if state else None,last_success_at=state.last_success_at if state else None,last_error_code=state.last_error_code if state else None,deferred_count=state.deferred_count if state else 0,intake_failed_count=db.scalar(select(func.count()).select_from(GmailIntakeFailure).where(GmailIntakeFailure.status=='pending')))
@app.get('/api/dashboard/stats',dependencies=[Depends(principal)])
def stats(db:Session=Depends(get_db)):
    records=db.scalars(select(Complaint).where(Complaint.canonical_case_id.is_(None))).all();work=[c for c in records if c.is_complaint is True];steps=[]
    for c in records:
        run=db.scalar(select(AgentRun).where(AgentRun.complaint_id==c.id).order_by(AgentRun.created_at.desc()).limit(1))
        if run:steps.extend(db.scalars(select(AgentStep).where(AgentStep.run_id==run.id)).all())
    sev_counts = {s: sum((c.policy_snapshot or {}).get('severity') == s for c in work) for s in ('critical', 'high', 'medium', 'low')}
    return dict(total=len(work),pending_review=sum(c.case_status=='pending_review' for c in work),insufficient_information=sum(c.case_status=='insufficient_information' for c in work),processed=sum(c.case_status=='processed' for c in work),workflow_counts={s:sum(c.workflow_status==s for c in work) for s in ('needs_review','waiting_customer','waiting_fulfillment','resolved','closed')},technical_failed=sum(c.is_complaint is not False and c.processing_status in ('failed','pending') for c in records),agent_counts={s:sum(x.status==s for x in steps) for s in ('running','failed','waiting_data')},severity_counts=sev_counts,urgent_count=sev_counts['critical']+sev_counts['high'])

@app.get('/api/reports/summary',dependencies=[Depends(principal)])
def reports_summary(db:Session=Depends(get_db)):
    records=db.scalars(select(Complaint).where(Complaint.canonical_case_id.is_(None))).all();work=[c for c in records if c.is_complaint is True]
    sev_counts = {s: sum((c.policy_snapshot or {}).get('severity') == s for c in work) for s in ('critical', 'high', 'medium', 'low')}
    triggers_count = {}
    auto_resolved = 0
    taken_over = 0
    for c in work:
        snap = c.policy_snapshot or {}
        if snap.get('case_report'):
            auto_resolved += 1
        if snap.get('taken_over_by'):
            taken_over += 1
        for reason in snap.get('escalation_reasons', []):
            code = reason.get('code', 'other')
            triggers_count[code] = triggers_count.get(code, 0) + 1
    return dict(
        total_cases=len(work),
        workflow_counts={s:sum(c.workflow_status==s for c in work) for s in ('needs_review','waiting_customer','waiting_fulfillment','resolved','closed')},
        severity_counts=sev_counts,
        urgent_count=sev_counts['critical'] + sev_counts['high'],
        escalation_rate=round(100 * (sev_counts['critical'] + sev_counts['high']) / max(len(work), 1), 1),
        automation_rate=round(100 * auto_resolved / max(len(work), 1), 1),
        taken_over_count=taken_over,
        top_escalation_triggers=[{'code': k, 'count': v} for k, v in sorted(triggers_count.items(), key=lambda x: x[1], reverse=True)[:5]]
    )

@app.get('/api/complaints',dependencies=[Depends(principal)])
def cases(queue:str='work',workflow_status:str|None=None,processing_status:str|None=None,complaint_type:str|None=None,case_status:str|None=None,severity:str|None=None,q:str=Query('',max_length=200),page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),db:Session=Depends(get_db)):
    if queue not in ('work','technical','urgent'):fail(422,'invalid_queue')
    query=select(Complaint).where(Complaint.canonical_case_id.is_(None))
    if queue=='work':
        query=query.where(Complaint.is_complaint.is_(True))
    elif queue=='urgent':
        query=query.where(Complaint.is_complaint.is_(True), Complaint.policy_snapshot['severity'].astext.in_(['critical','high']))
    else:
        query=query.where(Complaint.is_complaint.is_not(False),Complaint.processing_status.in_(['failed','pending','processing']))
    for field,value in [('workflow_status',workflow_status),('processing_status',processing_status),('complaint_type',complaint_type),('case_status',case_status)]:
        if value:query=query.where(getattr(Complaint,field)==value)
    if severity:
        query=query.where(Complaint.policy_snapshot['severity'].astext==severity)
    if q:query=query.where(or_(Complaint.email_subject.icontains(q,autoescape=True),Complaint.email_body.icontains(q,autoescape=True),Complaint.order_id.icontains(q,autoescape=True)))
    return {'items':[summary(db,c) for c in db.scalars(query.order_by(Complaint.updated_at.desc(),Complaint.id.desc()).offset((page-1)*page_size).limit(page_size)).all()],'total':db.scalar(select(func.count()).select_from(query.subquery())),'page':page,'page_size':page_size}
@app.get('/api/complaints/{cid}',dependencies=[Depends(principal)])
def case_detail(cid:int,db:Session=Depends(get_db)):return detail(db,get_case(db,cid))
@app.get('/api/complaints/{cid}/messages',dependencies=[Depends(principal)])
def messages(cid:int,db:Session=Depends(get_db)):return {'items':detail(db,get_case(db,cid))['messages']}
@app.get('/api/complaints/{cid}/audit',dependencies=[Depends(principal)])
def audits(cid:int,db:Session=Depends(get_db)):return {'items':detail(db,get_case(db,cid))['audit_events']}
@app.get('/api/complaints/{cid}/decisions',dependencies=[Depends(principal)])
def decisions(cid:int,db:Session=Depends(get_db)):return {'items':detail(db,get_case(db,cid))['decisions']}
@app.get('/api/orders',dependencies=[Depends(principal)])
def orders(q:str=Query('',max_length=200),page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),db:Session=Depends(get_db)):
    query=select(Order)
    if q:query=query.where(or_(Order.order_id.icontains(q,autoescape=True),Order.product_name.icontains(q,autoescape=True)))
    return {'items':[row(x) for x in db.scalars(query.order_by(Order.id).offset((page-1)*page_size).limit(page_size)).all()],'total':db.scalar(select(func.count()).select_from(query.subquery())),'page':page,'page_size':page_size}
@app.get('/api/integrations/intake-failures',dependencies=[Depends(principal)])
def failures(status:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),db:Session=Depends(get_db)):
    q=select(GmailIntakeFailure)
    if status:q=q.where(GmailIntakeFailure.status==status)
    return {'items':[row(f) for f in db.scalars(q.order_by(GmailIntakeFailure.last_attempt_at.desc()).offset((page-1)*page_size).limit(page_size)).all()],'total':db.scalar(select(func.count()).select_from(q.subquery())),'page':page,'page_size':page_size}
if (settings.frontend_dist/'index.html').is_file():
    from app.static import SPAStaticFiles
    app.mount('/',SPAStaticFiles(directory=settings.frontend_dist,html=True),name='frontend')
