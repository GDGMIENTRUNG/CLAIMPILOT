from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, func, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.config import settings
from app.database import get_db
from app.models import Complaint
from app.schemas import ComplaintDetail, ComplaintPage, Stats, SyncResult, Health, IntegrationStatus, CaseStatus, ComplaintType
from app.services.gmail import GmailService
from app.services.ai import get_ai_service
from app.services.errors import IntegrationError
from app.services.sync import synchronize, sync_lock, analyze_saved_complaint

app = FastAPI(title="ClaimPilot", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
DB = Annotated[Session, Depends(get_db)]
@app.exception_handler(SQLAlchemyError)
async def database_error(request, exc):
    return JSONResponse(status_code=503, content={"detail": "Database unavailable or schema not initialized. Check PostgreSQL and run migrations."})
@app.exception_handler(IntegrationError)
async def integration_error(request, exc):
    return JSONResponse(status_code=503, content={"detail": exc.code})
@app.get("/api/health", response_model=Health)
def health(db: DB):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
@app.get("/api/integrations/status", response_model=IntegrationStatus)
def integrations():
    return dict(gmail_configured=settings.token_path.is_file(), gemini_configured=bool(settings.gemini_api_key), ai_provider=settings.ai_provider, ai_model=settings.groq_model if settings.ai_provider == "groq" else settings.gemini_model, ai_configured=bool(settings.groq_api_key if settings.ai_provider == "groq" else settings.gemini_api_key), note="Configuration presence only; connectivity is verified during synchronization.")
@app.get("/api/dashboard/stats", response_model=Stats)
def stats(db: DB):
    counts = dict(db.execute(select(Complaint.case_status, func.count()).where(Complaint.is_complaint.is_(True)).group_by(Complaint.case_status)).all())
    return dict(total=sum(counts.values()), **{key: counts.get(key, 0) for key in ["pending_review", "insufficient_information", "processed"]})
@app.get("/api/complaints", response_model=ComplaintPage)
def complaints(db: DB, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), case_status: CaseStatus | None = None, complaint_type: ComplaintType | None = None):
    query = select(Complaint).where(Complaint.is_complaint.is_(True))
    if case_status:
        query = query.where(Complaint.case_status == case_status)
    if complaint_type:
        query = query.where(Complaint.complaint_type == complaint_type)
    total = db.scalar(select(func.count()).select_from(query.subquery()))
    items = db.scalars(query.order_by(Complaint.received_at.desc(), Complaint.id.desc()).offset((page-1)*page_size).limit(page_size)).all()
    return dict(items=items, total=total, page=page, page_size=page_size)
@app.get("/api/complaints/{complaint_id}", response_model=ComplaintDetail)
def detail(complaint_id: int, db: DB):
    record = db.get(Complaint, complaint_id)
    if record is None or not record.is_complaint:
        raise HTTPException(404, "Complaint not found")
    return record
@app.post("/api/gmail/sync", response_model=SyncResult)
def sync(db: DB):
    if not sync_lock.acquire(blocking=False):
        raise HTTPException(409, "A synchronization is already running")
    try:
        return synchronize(db, GmailService(), get_ai_service())
    finally:
        sync_lock.release()

@app.post("/api/complaints/{complaint_id}/analyze", response_model=ComplaintDetail)
def analyze_complaint(complaint_id: int, db: DB):
    if not sync_lock.acquire(blocking=False):
        raise HTTPException(409, "Another synchronization or analysis is already running")
    try:
        record = db.get(Complaint, complaint_id)
        if record is None:
            raise HTTPException(404, "Complaint not found")
        if record.case_status not in {"processing_failed", "processing"}:
            raise HTTPException(409, "This complaint already has a completed analysis")
        return analyze_saved_complaint(db, record, get_ai_service())
    finally:
        sync_lock.release()
