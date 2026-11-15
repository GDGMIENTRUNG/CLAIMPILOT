"""Staff sessions: server-side revocation, exact origins and CSRF on mutations."""
import hashlib
import hmac
import json
import os
import secrets
import time
from ipaddress import ip_address
from urllib.parse import urlsplit
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import Depends, HTTPException, Request, Response, APIRouter
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.config import settings, ROOT
from app.database import get_db
from app.models import StaffSession

router=APIRouter(prefix='/api/auth',tags=['auth'])
hasher=PasswordHasher()
attempts=defaultdict(deque)
attempt_lock=Lock()

def now(): return datetime.now(timezone.utc)
def digest(value): return hashlib.sha256(value.encode()).hexdigest()
def fail(status,code): raise HTTPException(status,detail=code)
def credentials():
    p=Path(settings.local_credentials_path)
    if not p.is_absolute(): p=ROOT/p
    try: return json.loads(p.read_text())
    except (OSError, ValueError): fail(503,'staff_account_not_initialized_run_local_setup')

def check_origin(request):
    allowed={settings.public_base_url.rstrip('/'),settings.frontend_origin.rstrip('/')}
    if request.headers.get('origin') not in allowed: fail(403,'origin_invalid')

def principal(request:Request,db:Session=Depends(get_db)):
    token=request.cookies.get('cp_session','')
    session=db.scalar(select(StaffSession).where(StaffSession.token_hash==digest(token))) if token else None
    if session is None or session.revoked_at or session.expires_at<=now(): fail(401,'session_expired')
    if request.method not in ('GET','HEAD','OPTIONS'):
        check_origin(request)
        csrf=request.headers.get('x-csrf-token','')
        if not csrf or not hmac.compare_digest(digest(csrf),session.csrf_hash): fail(403,'csrf_invalid')
    return session

def session_response(session,token):
    return dict(username=session.staff_id,csrf_token=digest('csrf:'+token),expires_at=session.expires_at)

class Login(BaseModel):
    model_config=ConfigDict(extra='forbid')
    username:str=Field(min_length=1,max_length=100)
    password:str=Field(min_length=1,max_length=256)

def demo_login_enabled(request:Request):
    if not settings.local_demo_login or os.environ.get('K_SERVICE') or os.environ.get('CLOUD_RUN_JOB'):return False
    local_hosts={'localhost','127.0.0.1','::1'}
    base=urlsplit(settings.public_base_url)
    if base.scheme!='http' or base.hostname not in local_hosts or request.url.hostname not in local_hosts:return False
    if any(header in request.headers for header in ('forwarded','x-forwarded-for','x-forwarded-host','cf-connecting-ip','cf-ray')):return False
    try:return bool(request.client and ip_address(request.client.host).is_loopback)
    except ValueError:return False

@router.get('/config')
def login_config(request:Request):
    return {'demo_login':demo_login_enabled(request)}

@router.post('/login')
def login(data:Login,request:Request,response:Response,db:Session=Depends(get_db)):
    check_origin(request)
    ip=request.client.host if request.client else 'unknown'
    with attempt_lock:
        q=attempts[ip]
        while q and q[0]<time.monotonic()-900:q.popleft()
        if len(q)>=5:fail(429,'login_rate_limited')
    demo=demo_login_enabled(request)
    if demo:
        valid=True;staff_id=data.username
    else:
        config=credentials();staff_id=config['username']
        try:valid=hasher.verify(config['password_hash'],data.password) and hmac.compare_digest(config['username'].encode(),data.username.encode())
        except (VerificationError,InvalidHashError):valid=False
    if not valid:
        with attempt_lock:attempts[ip].append(time.monotonic())
        fail(401,'invalid_credentials')
    token=secrets.token_urlsafe(32)
    issued=now()
    s=StaffSession(token_hash=digest(token),csrf_hash=digest(digest('csrf:'+token)),staff_id=staff_id,created_at=issued,expires_at=issued+timedelta(hours=8))
    db.add(s);db.commit()
    response.set_cookie('cp_session',token,max_age=28800,httponly=True,secure=settings.session_cookie_secure,samesite='lax',path='/')
    return session_response(s,token)

@router.get('/me')
def me(request:Request,s:StaffSession=Depends(principal)):
    return session_response(s,request.cookies['cp_session'])

@router.post('/logout',status_code=204)
def logout(response:Response,s:StaffSession=Depends(principal),db:Session=Depends(get_db)):
    s.revoked_at=now();db.commit();response.delete_cookie('cp_session',path='/')

def preview_signature(payload):
    key=credentials()['preview_key']
    return hmac.new(key.encode(),json.dumps(payload,sort_keys=True,separators=(',',':'),default=str).encode(),hashlib.sha256).hexdigest()
