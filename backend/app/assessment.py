"""Bounded, persisted AI attempts plus deterministic order/policy assessment."""
from datetime import datetime,timedelta,date
from uuid import uuid4,UUID
import hashlib,json
from fastapi import APIRouter,Depends
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Complaint,Order,CaseMessage,TextAnalysisRun,AgentRun,AgentStep
from app.knowledge import Input,config,retrieve,valid_refs
from app.security import principal,fail,now
from app.workspace import get_case,mutate,reopen_fields,row,detail,audit,run_json,encode
from app.services.ai import get_ai_service
from app.services.errors import IntegrationError
from app.services.risk import assess_case_risk
from app.config import settings

router=APIRouter(prefix='/api',dependencies=[Depends(principal)])
POLICY_VERSION='demo-v2'

def evaluate(db,c):
    order=db.scalar(select(Order).where(Order.order_id==c.order_id)) if c.order_id else None
    c.verified_order_id=order.id if order else None
    matched=bool(order and order.customer_email.casefold()==c.sender_email.casefold())
    c.sender_matches_order=matched if order else None
    if c.ownership_status!='manually_verified':c.ownership_status='email_matched' if matched else ('mismatch' if order else 'unverified')
    c.verification_status='delivered' if order and order.actual_delivery_date else ('not_delivered' if order else 'order_not_found')
    result='insufficient_information';reason='Cần nhân viên kiểm tra thêm dữ liệu.';missing=[]
    # Policy date is the first complaint date, never the clock at a later retry.
    when=c.received_at.date()
    if not order:result='order_not_found';reason='Chưa tìm thấy đơn hàng. Vui lòng bổ sung mã đơn.';missing=['order_id']
    elif c.complaint_type=='late_delivery':
        if not order.actual_delivery_date or not order.expected_delivery_date:missing=['delivery_date'];reason='Thiếu ngày giao thực tế/dự kiến.'
        elif order.actual_delivery_date>order.expected_delivery_date:result='eligible_for_review';reason='Đơn giao trễ; có thể xem xét hoàn phí vận chuyển.'
        else:result='not_eligible';reason='Ngày giao không trễ so với dự kiến.'
    elif c.complaint_type=='not_received':
        if order.actual_delivery_date:reason='Đơn có dấu hiệu đã giao nhưng khách báo chưa nhận; cần đối soát.';missing=['delivery_proof']
        elif order.expected_delivery_date and when>order.expected_delivery_date+timedelta(days=2):result='eligible_for_review';reason='Chưa nhận hàng sau thời gian chờ; cần điều tra vận chuyển.'
        else:reason='Cần kiểm tra lịch giao và cập nhật từ vận chuyển.';missing=['carrier_update']
    elif c.complaint_type in ('damaged_item','wrong_item'):
        reason='Cần bằng chứng về sản phẩm để nhân viên đánh giá.';missing=['product_images']
    elif c.complaint_type=='refund_request':
        if order.actual_delivery_date:
            result='eligible_for_review' if (when-order.actual_delivery_date).days<=7 else 'not_eligible'
            reason='Trong thời hạn xem xét7 ngày.' if result=='eligible_for_review' else 'Đã quá thời hạn demo7 ngày; nhân viên có thể xem xét ngoại lệ.'
            if order.total_amount is None:missing=['total_amount'];reason+=' Chưa có tổng tiền, không tự ước tính.'
        else:reason='Cần kiểm tra trạng thái giao hàng và căn cứ hoàn tiền.';missing=['delivery_status']
    c.policy_result=result;c.policy_reason=reason;c.policy_version=POLICY_VERSION
    old=c.policy_snapshot or {}
    inbounds = db.scalars(select(CaseMessage).where(CaseMessage.complaint_id==c.id, CaseMessage.direction=='inbound')).all() if c.id else []
    refs = retrieve(db, (c.complaint_type or '') + ' ' + (c.email_subject or '')) if c.complaint_type else []
    sev, reasons, takeover_req = assess_case_risk(c, order, inbounds, len(refs))
    c.policy_snapshot=dict(schema_version=1,data_source='manual' if old.get('manual_overrides') else 'ai',assessment_received_at=c.received_at.isoformat(),order_snapshot=row(order) if order else {},policy_version=POLICY_VERSION,result=result,reason=reason,missing_fields=missing,next_action='Nhân viên xem xét' if not missing else 'Bổ sung thông tin',manual_overrides=old.get('manual_overrides',{}),ownership_confirmation=old.get('ownership_confirmation'),text_analysis_id=str(c.latest_text_analysis_id) if c.latest_text_analysis_id else None,evidence_analysis_id=None,severity=sev,escalation_reasons=reasons,requires_immediate_takeover=takeover_req,taken_over_by=old.get('taken_over_by'),taken_over_at=old.get('taken_over_at'),takeover_note=old.get('takeover_note'),case_report=old.get('case_report'))
    return order

class Review(Input):
    expected_case_version:int=Field(ge=1)
    note:str=Field(min_length=1,max_length=2000)
    is_complaint:bool|None=None
    order_id:str|None=Field(default=None,max_length=100)
    complaint_type:str|None=None
    requested_action:str|None=None
    ownership_confirmation:dict|None=None
    acknowledge_manual_review:bool=False

@router.patch('/complaints/{case_id}/review')
def review(case_id:int,data:Review,s=Depends(principal),db:Session=Depends(get_db)):
    allowed_types={'late_delivery','not_received','damaged_item','wrong_item','refund_request','other'}
    allowed_actions={'shipping_fee_refund','order_refund','replacement','request_information','other'}
    if data.complaint_type is not None and data.complaint_type not in allowed_types:fail(422,'invalid_complaint_type')
    if data.requested_action is not None and data.requested_action not in allowed_actions:fail(422,'invalid_requested_action')
    with mutate(db,case_id,data.expected_case_version,s.staff_id,data.note,'manual_reviewed') as c:
        changed=False;overrides=dict((c.policy_snapshot or {}).get('manual_overrides',{}))
        for k,v in data.model_dump(include={'is_complaint','order_id','complaint_type','requested_action'},exclude_unset=True).items():
            if k=='is_complaint' and v is None:fail(422,'classification_required')
            if getattr(c,k)!=v:changed=True
            if k=='order_id' and c.order_id!=v:c.ownership_status='unverified'
            setattr(c,k,v);overrides[k]=v
        if data.ownership_confirmation:
            proof=data.ownership_confirmation
            if set(proof)-{'verified','reason'} or proof.get('verified') is not True or not str(proof.get('reason','')).strip():fail(422,'ownership_reason_required')
            if not c.order_id:fail(409,'order_not_found')
            c.ownership_status='manually_verified';changed=True
        c.policy_snapshot={**(c.policy_snapshot or {}),'manual_overrides':overrides}
        order=evaluate(db,c)
        if data.ownership_confirmation:
            if not order:fail(409,'order_not_found')
            c.policy_snapshot={**c.policy_snapshot,'ownership_confirmation':dict(actor=s.staff_id,reason=data.ownership_confirmation['reason'],confirmed_at=now().isoformat(),order_internal_id=order.id,correspondent=c.sender_email)}
        if changed:c.current_decision_id=None;reopen_fields(c)
        if data.acknowledge_manual_review:c.needs_manual_review=False
        c.processing_status='completed';c.case_status='pending_review' if c.is_complaint else 'processed'
    return detail(db,c)

class Reassess(Input):
    expected_case_version:int=Field(ge=1)
    note:str=Field(default='Đánh giá lại theo dữ liệu hiện tại',min_length=1,max_length=2000)
@router.post('/complaints/{case_id}/reassess')
def reassess(case_id:int,data:Reassess,s=Depends(principal),db:Session=Depends(get_db)):
    with mutate(db,case_id,data.expected_case_version,s.staff_id,data.note,'assessment_applied') as c:
        evaluate(db,c);c.current_decision_id=None;reopen_fields(c)
    return detail(db,c)

class TakeoverInput(Input):
    expected_case_version:int=Field(ge=1)
    note:str=Field(default='Nhân viên tiếp quản xử lý hồ sơ',min_length=1,max_length=2000)

@router.post('/complaints/{case_id}/takeover')
def takeover(case_id:int,data:TakeoverInput,s=Depends(principal),db:Session=Depends(get_db)):
    with mutate(db,case_id,data.expected_case_version,s.staff_id,data.note,'case_taken_over') as c:
        snap=dict(c.policy_snapshot or {})
        snap['taken_over_by']=s.staff_id
        snap['taken_over_at']=now().isoformat()
        snap['takeover_note']=data.note
        c.policy_snapshot=snap
    return detail(db,c)

@router.post('/complaints/{case_id}/release-takeover')
def release_takeover(case_id:int,data:TakeoverInput,s=Depends(principal),db:Session=Depends(get_db)):
    with mutate(db,case_id,data.expected_case_version,s.staff_id,data.note,'case_takeover_released') as c:
        snap=dict(c.policy_snapshot or {})
        snap.pop('taken_over_by',None)
        snap.pop('taken_over_at',None)
        snap['takeover_note']=data.note
        c.policy_snapshot=snap
    return detail(db,c)

def step(db,run,role,status,output=None,refs=None,error=None,skip=None):
    t=now();o=AgentStep(run_id=run.id,role=role,attempt=1,status=status,source_refs=refs or [],input_snapshot={'basis_case_version':run.basis_case_version},output=output,confidence=None,error_code=error,skip_reason=skip,started_at=t,finished_at=t)
    db.add(o);db.commit();return o

def analyze(db,c,expected):
    from app.workspace import version
    cfg=config(db);c=get_case(db,c.id,True);version(c,expected)
    if c.workflow_status=='closed':fail(409,'invalid_case_state')
    active=db.scalar(select(AgentRun.id).where(AgentRun.complaint_id==c.id,AgentRun.status.in_(['queued','running'])))
    if active:fail(409,'agent_busy')
    basis=c.case_version;message=db.scalar(select(CaseMessage).where(CaseMessage.complaint_id==c.id,CaseMessage.direction=='inbound').order_by(CaseMessage.occurred_at.desc(),CaseMessage.id.desc()).limit(1))
    if not message:fail(409,'inbound_message_missing')
    run=AgentRun(complaint_id=c.id,basis_case_version=basis,settings_version_id=cfg.id,status='running',required_roles=['intake_classification','order_lookup','policy_assessment'],trigger='retry')
    db.add(run);db.flush()
    text_run=TextAnalysisRun(complaint_id=c.id,message_id=message.id,basis_case_version=basis,provider=settings.ai_provider,model=settings.groq_model if settings.ai_provider=='groq' else settings.gemini_model,input_hash=hashlib.sha256((message.subject+'\n'+message.body).encode()).hexdigest(),input_snapshot={'schema_version':1,'source':'live','message_ids':[str(message.id)],'basis_case_version':basis,'manual_overrides':(c.policy_snapshot or {}).get('manual_overrides',{}),'order_internal_id':c.verified_order_id,'truncated':len(message.body)>60000})
    text_run.started_at=now()
    db.add(text_run);db.commit()
    try:analysis=get_ai_service().analyze(message.subject,message.body)
    except IntegrationError as exc:
        c=db.scalar(select(Complaint).where(Complaint.id==c.id).with_for_update().execution_options(populate_existing=True))
        if c.case_version!=basis:
            text_run.status='failed';text_run.error_code=exc.code;text_run.finished_at=now()
            run.status='stale';run.finished_at=now();db.commit()
            step(db,run,'intake_classification','stale',error=exc.code)
            return run
        text_run.status='failed';text_run.error_code=exc.code;text_run.finished_at=now();c.processing_status='failed';c.processing_error=exc.code;c.case_status='processing_failed'
        run.status='review_required';run.finished_at=now();db.commit()
        step(db,run,'intake_classification','failed',error=exc.code)
        for role in ('order_lookup','policy_assessment'):step(db,run,role,'waiting_data',{'missing_fields':['validated_analysis']})
        step(db,run,'evidence_analysis','skipped',skip='Chưa có kết quả phân loại hợp lệ')
        return run
    # Provider calls never hold the case lock. Reacquire it before comparing the
    # basis and applying output so inbound/manual edits cannot slip between them.
    c=db.scalar(select(Complaint).where(Complaint.id==c.id).with_for_update().execution_options(populate_existing=True))
    text_run.output=analysis.model_dump()
    if c.case_version!=basis:
        text_run.status='stale';text_run.finished_at=now();run.status='stale';run.finished_at=now();db.commit();step(db,run,'intake_classification','stale',analysis.model_dump());return run
    manual=(c.policy_snapshot or {}).get('manual_overrides',{})
    for field,key in [('is_complaint','is_complaint'),('complaint_type','complaint_type'),('order_id','order_id'),('requested_action','requested_action'),('ai_summary','summary'),('priority','priority'),('missing_information','missing_information')]:
        if field not in manual:setattr(c,field,getattr(analysis,key))
    c.latest_text_analysis_id=text_run.id;c.case_version+=1;c.current_decision_id=None;reopen_fields(c)
    evaluate(db,c);c.processing_status='completed';c.processing_error=None;c.case_status='pending_review' if c.is_complaint else 'processed'
    text_run.status='completed';text_run.finished_at=now();text_run.applied_case_version=c.case_version;message.analysis=analysis.model_dump();message.processing_status='completed'
    audit(db,c,'assessment_applied','agent:intake_classification','Phân tích đã validate',after={'case_version':c.case_version})
    refs=retrieve(db,(c.complaint_type or '')+' '+message.subject)
    run.status='running';db.commit()
    step(db,run,'intake_classification','completed',{**analysis.model_dump(),'confidence_status':'not_calibrated'})
    step(db,run,'order_lookup','completed' if c.verified_order_id else 'waiting_data',{'order_id':c.order_id,'ownership_status':c.ownership_status,'missing_fields':[] if c.verified_order_id else ['order_id']})
    step(db,run,'policy_assessment','completed' if refs else 'waiting_data',{'result':c.policy_result,'reason':c.policy_reason,'missing_fields':[] if refs else ['approved_knowledge']},refs)
    from app.evidence import assets_for,analyze_images
    available=assets_for(db,c)
    if available and 'evidence_analysis' in cfg.optional_roles:
        image_run=analyze_images(db,c,c.case_version)
        refs_assets=[dict(kind='asset',id=str(a.id),version=str(a.object_generation),digest=a.sha256,excerpt=None) for a in available[:4]]
        step(db,run,'evidence_analysis','completed' if image_run.status=='completed' else 'failed',{'consistency':image_run.consistency,'observations':image_run.observations,'limitations':image_run.limitations},refs_assets,error=image_run.error_code)
    elif c.complaint_type in ('damaged_item','wrong_item'):
        step(db,run,'evidence_analysis','waiting_data',{'missing_fields':['product_images'],'reason':'Chưa đủ ảnh hoặc vai trò ảnh đang tắt; cần nhân viên xem xét'})
    else:step(db,run,'evidence_analysis','skipped',skip='Chưa có ảnh hợp lệ để phân tích; tiếp tục kiểm tra thủ công')
    required=list(db.scalars(select(AgentStep).where(AgentStep.run_id==run.id,AgentStep.role.in_(run.required_roles))).all())
    incomplete=any(not any(s.role==role and s.status=='completed' for s in required) for role in run.required_roles)
    evidence=db.scalar(select(AgentStep).where(AgentStep.run_id==run.id,AgentStep.role=='evidence_analysis'))
    # Providers currently expose no calibrated confidence. A configured threshold
    # must therefore request staff review rather than invent a passing score.
    run.status='review_required' if incomplete or c.policy_snapshot.get('missing_fields') or not refs or cfg.review_threshold is not None or (evidence and evidence.status in ('failed','waiting_data')) else 'completed'
    run.finished_at=now()
    db.commit()
    return run

@router.post('/complaints/{case_id}/agent-runs',status_code=202)
def start_run(case_id:int,data:Reassess,s=Depends(principal),db:Session=Depends(get_db)):
    c=get_case(db,case_id);r=analyze(db,c,data.expected_case_version);return {'run':run_json(db,r),'case_version':c.case_version}
@router.post('/complaints/{case_id}/analyze')
def retry_analysis(case_id:int,s=Depends(principal),db:Session=Depends(get_db)):
    c=get_case(db,case_id);analyze(db,c,c.case_version);return detail(db,c)
@router.get('/complaints/{case_id}/agent-runs')
def get_runs(case_id:int,db:Session=Depends(get_db)):
    c=get_case(db,case_id)
    return {'items':[run_json(db,r) for r in db.scalars(select(AgentRun).where(AgentRun.complaint_id==c.id).order_by(AgentRun.created_at.desc())).all()]}
@router.get('/complaints/{case_id}/sources')
def sources(case_id:int,db:Session=Depends(get_db)):
    c=get_case(db,case_id);refs=[]
    for st in db.scalars(select(AgentStep).join(AgentRun).where(AgentRun.complaint_id==c.id).order_by(AgentStep.created_at.desc())).all():
        for r in st.source_refs:
            if r['id'] not in {x['id'] for x in refs}:refs.append({**r,'eligible':valid_refs(db,[r])})
    return {'items':refs,'warnings':[] if refs else ['Chưa có nguồn KB đã duyệt phù hợp']}

@router.get('/policies')
def policies():return {'items':[{'version':POLICY_VERSION,'label':'Chính sách mẫu mini hackathon','rules_summary':['Giao trễ: xem xét phí vận chuyển','Chưa nhận: điều tra sau2 ngày','Hư hỏng/sai hàng: cần bằng chứng','Hoàn tiền: xem xét7 ngày, không tự giao dịch'],'source_status':'demo_policy'}]}
