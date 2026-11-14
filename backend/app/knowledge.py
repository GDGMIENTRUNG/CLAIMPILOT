"""Versioned, staff-approved knowledge and business settings."""
import hashlib,json
from datetime import datetime
from uuid import UUID,uuid4
from typing import Literal
from fastapi import APIRouter,Depends,Query
from pydantic import BaseModel,ConfigDict,Field,field_validator
from sqlalchemy import select,func,or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import BusinessSettings,SettingsVersion,KnowledgeArticle,KnowledgeRevision
from app.security import principal,fail,now
from app.workspace import row,encode

router=APIRouter(prefix='/api',dependencies=[Depends(principal)])
class Input(BaseModel):
    model_config=ConfigDict(extra='forbid',str_strip_whitespace=True)

class BusinessInput(Input):
    expected_revision:int=Field(ge=0)
    display_name:str|None=Field(default=None,min_length=1,max_length=200)
    language:Literal['vi','en']|None=None
    tone:Literal['neutral','friendly','formal']|None=None
    note:str=Field(min_length=1,max_length=2000)
class AgentInput(Input):
    expected_revision:int=Field(ge=1)
    optional_roles:list[Literal['evidence_analysis']]=Field(max_length=1)
    review_threshold:float|None=Field(default=None,ge=0,le=1)
    note:str=Field(min_length=1,max_length=2000)

def config(db,required=True):
    singleton=db.get(BusinessSettings,1)
    if not singleton:
        if required:fail(503,'config_unavailable')
        return None
    return db.get(SettingsVersion,singleton.current_version_id)

def settings_json(v):
    d=row(v);d['settings_version_id']=d['id'];d['updated_at']=d['created_at']
    d.update(mandatory_roles=['intake_classification','order_lookup','policy_assessment','reply_writer','safety_quality'],guardrails={'staff_decision':True,'confirmed_send':True,'ownership':True,'source_validation':True})
    return d

@router.get('/settings/business')
@router.get('/settings/agents')
def read_settings(db:Session=Depends(get_db)):return settings_json(config(db))

def save_config(db,data,actor,initial=False):
    # Serialize initialization and cross-panel edits without changing the schema.
    from sqlalchemy import text
    db.execute(text('SELECT pg_advisory_xact_lock(17484401)'))
    v=config(db,False)
    if data.expected_revision!=(v.revision if v else 0):fail(409,'settings_conflict')
    values={k:getattr(v,k) for k in ('display_name','language','tone','optional_roles','review_threshold')} if v else {}
    values.update(data.model_dump(exclude={'expected_revision','note'},exclude_unset=True))
    if not all(values.get(k) for k in ('display_name','language','tone')):fail(422,'business_setup_required')
    new=SettingsVersion(**values,revision=(v.revision+1 if v else 1),actor=actor,note=data.note)
    db.add(new);db.flush()
    singleton=db.get(BusinessSettings,1)
    if singleton:singleton.current_version_id=new.id;singleton.updated_at=now()
    else:db.add(BusinessSettings(id=1,current_version_id=new.id))
    db.commit();return settings_json(new)

@router.patch('/settings/business')
def update_business(data:BusinessInput,s=Depends(principal),db:Session=Depends(get_db)):
    return save_config(db,data,s.staff_id)
@router.patch('/settings/agents')
def update_agents(data:AgentInput,s=Depends(principal),db:Session=Depends(get_db)):
    config(db);return save_config(db,data,s.staff_id)

class ArticleInput(Input):
    title:str=Field(min_length=1,max_length=300)
    body:str=Field(min_length=1,max_length=50000)
    topic:str=Field(min_length=1,max_length=100)
    source_label:str=Field(min_length=1,max_length=200)
    source_reference:str|None=Field(default=None,max_length=2048)
    valid_until:datetime|None=None
    review_due_at:datetime|None=None
    @field_validator('valid_until','review_due_at')
    @classmethod
    def aware(cls,v):
        if v is not None and v.tzinfo is None:raise ValueError('Timezone required')
        return v
class RevisionInput(ArticleInput):
    expected_revision:int=Field(ge=1)
class ArticlePatch(Input):
    expected_updated_at:datetime
    title:str|None=Field(default=None,min_length=1,max_length=300)
    body:str|None=Field(default=None,min_length=1,max_length=50000)
    topic:str|None=Field(default=None,min_length=1,max_length=100)
    source_label:str|None=Field(default=None,min_length=1,max_length=200)
    source_reference:str|None=Field(default=None,max_length=2048)
    valid_until:datetime|None=None
    review_due_at:datetime|None=None
    @field_validator('expected_updated_at','valid_until','review_due_at')
    @classmethod
    def aware(cls,v):
        if v is not None and v.tzinfo is None:raise ValueError('Timezone required')
        return v
class Transition(Input):
    expected_updated_at:datetime
    note:str=Field(default='Submitted for review',min_length=1,max_length=2000)
    has_conflict:bool|None=None

def eligible(db,r):
    a=db.get(KnowledgeArticle,r.article_id)
    return (r.status=='approved' and a.current_published_revision_id==r.id and not r.has_conflict
            and (r.valid_until is None or r.valid_until>now()) and (r.review_due_at is None or r.review_due_at>now()))

def ref(r):
    return dict(kind='knowledge',id=str(r.id),version=str(r.revision),digest=hashlib.sha256(r.body.encode()).hexdigest(),excerpt=r.body[:1000],title=r.title,article_id=str(r.article_id))

def retrieve(db,query,limit=5):
    words=[w for w in query.split() if len(w)>2][:12]
    q=select(KnowledgeRevision).where(KnowledgeRevision.status=='approved')
    if not words:return []
    q=q.where(or_(*[or_(KnowledgeRevision.title.icontains(w,autoescape=True),KnowledgeRevision.body.icontains(w,autoescape=True),KnowledgeRevision.topic.icontains(w,autoescape=True)) for w in words]))
    return [ref(r) for r in db.scalars(q.order_by(KnowledgeRevision.updated_at.desc())).all() if eligible(db,r)][:limit]

def valid_refs(db,refs):
    for source in refs:
        if source.get('kind')=='knowledge':
            try:r=db.get(KnowledgeRevision,UUID(source['id']))
            except (ValueError,KeyError):return False
            if not r or not eligible(db,r) or str(r.article_id)!=source.get('article_id') or ref(r)['digest']!=source.get('digest') or str(r.revision)!=source.get('version'):return False
    return True

def event(db,a,r,action,actor,note):
    a.events=[*(a.events or []),dict(event_id=str(uuid4()),revision_id=str(r.id),action=action,actor=actor,at=now().isoformat(),note=note,after={'status':r.status,'has_conflict':r.has_conflict})]
    a.updated_at=now()

@router.get('/knowledge')
def articles(q:str=Query('',max_length=200),topic:str|None=None,status:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),db:Session=Depends(get_db)):
    query=select(KnowledgeRevision)
    if q:query=query.where(or_(KnowledgeRevision.title.icontains(q,autoescape=True),KnowledgeRevision.body.icontains(q,autoescape=True)))
    if topic:query=query.where(KnowledgeRevision.topic==topic)
    if status:query=query.where(KnowledgeRevision.status==status)
    total=db.scalar(select(func.count()).select_from(query.subquery()))
    return dict(items=[row(r) for r in db.scalars(query.order_by(KnowledgeRevision.updated_at.desc()).offset((page-1)*page_size).limit(page_size)).all()],total=total,page=page,page_size=page_size)

@router.post('/knowledge',status_code=201)
def create_article(data:ArticleInput,s=Depends(principal),db:Session=Depends(get_db)):
    a=KnowledgeArticle();db.add(a);db.flush()
    r=KnowledgeRevision(**data.model_dump(),article_id=a.id,revision=1,author=s.staff_id)
    db.add(r);db.flush();event(db,a,r,'created',s.staff_id,'Created draft');db.commit()
    return dict(article_id=str(a.id),revision=row(r))

@router.get('/knowledge/{article_id}')
def article(article_id:UUID,db:Session=Depends(get_db)):
    a=db.get(KnowledgeArticle,article_id)
    if not a:fail(404,'knowledge_not_found')
    return {**row(a),'article_id':str(a.id),'revisions':[row(r) for r in db.scalars(select(KnowledgeRevision).where(KnowledgeRevision.article_id==a.id).order_by(KnowledgeRevision.revision.desc())).all()]}

@router.get('/knowledge/{article_id}/revisions/{revision_id}')
def revision(article_id:UUID,revision_id:UUID,db:Session=Depends(get_db)):
    r=db.get(KnowledgeRevision,revision_id)
    if not r or r.article_id!=article_id:fail(404,'knowledge_not_found')
    return {**row(r),'eligible':eligible(db,r)}

@router.post('/knowledge/{article_id}/revisions',status_code=201)
def new_revision(article_id:UUID,data:RevisionInput,s=Depends(principal),db:Session=Depends(get_db)):
    a=db.scalar(select(KnowledgeArticle).where(KnowledgeArticle.id==article_id).with_for_update())
    if not a:fail(404,'knowledge_not_found')
    latest=db.scalar(select(func.max(KnowledgeRevision.revision)).where(KnowledgeRevision.article_id==a.id))
    if latest!=data.expected_revision:fail(409,'knowledge_conflict')
    r=KnowledgeRevision(**data.model_dump(exclude={'expected_revision'}),article_id=a.id,revision=latest+1,author=s.staff_id)
    db.add(r);db.flush();event(db,a,r,'revision_created',s.staff_id,'New draft revision');db.commit()
    return dict(article_id=str(a.id),revision=row(r))

@router.patch('/knowledge/{article_id}/revisions/{revision_id}')
def edit_revision(article_id:UUID,revision_id:UUID,data:ArticlePatch,s=Depends(principal),db:Session=Depends(get_db)):
    r=db.scalar(select(KnowledgeRevision).where(KnowledgeRevision.id==revision_id,KnowledgeRevision.article_id==article_id).with_for_update())
    if not r:fail(404,'knowledge_not_found')
    if r.status!='draft':fail(409,'invalid_knowledge_state')
    if r.updated_at!=data.expected_updated_at:fail(409,'knowledge_conflict')
    for k,v in data.model_dump(exclude={'expected_updated_at'},exclude_unset=True).items():
        if v is None and k in ('title','body','topic','source_label'):fail(422,'invalid_knowledge_content')
        setattr(r,k,v)
    r.updated_at=now();event(db,db.get(KnowledgeArticle,article_id),r,'draft_edited',s.staff_id,'Updated draft');db.commit();return row(r)

@router.post('/knowledge/{article_id}/revisions/{revision_id}/{action}')
def transition(article_id:UUID,revision_id:UUID,action:Literal['submit','approve','archive','conflict'],data:Transition,s=Depends(principal),db:Session=Depends(get_db)):
    a=db.scalar(select(KnowledgeArticle).where(KnowledgeArticle.id==article_id).with_for_update())
    r=db.scalar(select(KnowledgeRevision).where(KnowledgeRevision.id==revision_id,KnowledgeRevision.article_id==article_id).with_for_update())
    if not a or not r:fail(404,'knowledge_not_found')
    if r.updated_at!=data.expected_updated_at:fail(409,'knowledge_conflict')
    if action=='submit':
        if r.status!='draft':fail(409,'invalid_knowledge_state')
        r.status='pending_review'
    elif action=='approve':
        if r.status!='pending_review' or r.has_conflict or any(t is not None and t<=now() for t in (r.valid_until,r.review_due_at)):fail(409,'invalid_knowledge_state')
        r.status='approved';r.approved_by=s.staff_id;r.approved_at=now();a.current_published_revision_id=r.id
    elif action=='archive':
        r.status='archived'
        if a.current_published_revision_id==r.id:a.current_published_revision_id=None
    else:
        if data.has_conflict is None:fail(422,'conflict_flag_required')
        r.has_conflict=data.has_conflict;r.conflict_note=data.note
    r.updated_at=now();event(db,a,r,action,s.staff_id,data.note);db.commit();return row(r)
