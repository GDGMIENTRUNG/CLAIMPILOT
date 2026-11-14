"""Explicit local account setup. Never runs as application startup."""
import json,os,secrets
from pathlib import Path
from app.config import ROOT,settings
from app.security import hasher
def setup():
    if os.getenv('K_SERVICE'):raise SystemExit('Local setup is not available in Cloud Run')
    p=Path(settings.local_credentials_path)
    if not p.is_absolute():p=ROOT/p
    if p.exists():
        print('Existing local account preserved:',p);return
    p.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    password=secrets.token_urlsafe(12)
    values=dict(username='admin',password_hash=hasher.hash(password),preview_key=secrets.token_urlsafe(48),local_password=password)
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump(values,f)
    print('Local account created. Username: admin. Password stored privately in',p)
if __name__=='__main__':setup()
