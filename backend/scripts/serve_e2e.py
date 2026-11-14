"""Isolated real API/SQL server for browser acceptance; no live credentials.

Run only through playwright.workspace.config.ts. Owns one random SQL schema,
never application tables. Removes its schema and temporary credentials on exit.
"""
import json
import signal
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.config import settings


def main():
    # Uvicorn replays termination signals after shutdown. Convert that replay
    # into a normal exit so the outer finally can remove this test's schema.
    def stop(signum,frame):
        raise SystemExit(0)
    signal.signal(signal.SIGTERM,stop)
    signal.signal(signal.SIGINT,stop)
    # Refuse remote databases: this launcher is explicitly for local testing.
    url=make_url(settings.database_url)
    if url.host not in ('localhost','127.0.0.1','::1'):
        raise RuntimeError('Browser acceptance requires a local PostgreSQL database')
    schema='e2e_'+uuid4().hex
    admin=create_engine(url)
    with TemporaryDirectory(prefix='claimpilot-browser-') as private:
        private_path=Path(private)
        settings.database_url=url.update_query_dict({'options':f'-csearch_path={schema}'}).render_as_string(hide_password=False)
        settings.public_base_url='http://127.0.0.1:8082'
        settings.frontend_origin=settings.public_base_url
        settings.session_cookie_secure=False
        settings.gemini_api_key='';settings.groq_api_key=''
        settings.google_client_id='';settings.google_client_secret=''
        settings.gmail_token_path=str(private_path/'absent-gmail-token.json')
        settings.enable_gmail_write=False
        settings.local_credentials_path=str(private_path/'staff.json')
        from app.security import hasher,now
        credentials=Path(settings.local_credentials_path)
        credentials.write_text(json.dumps({'username':'browser-tester','password_hash':hasher.hash('synthetic-browser-password'),'preview_key':uuid4().hex}))
        credentials.chmod(0o600)
        from app.database import Base,engine
        from app.models import Complaint,CaseMessage
        from app.main import app
        import uvicorn
        try:
            with admin.begin() as connection:
                connection.execute(text(f'CREATE SCHEMA "{schema}"'))
                connection.execute(text(f"COMMENT ON SCHEMA \"{schema}\" IS 'ClaimPilot synthetic browser acceptance; scripts.serve_e2e'"))
            # Metadata DDL is confined to this uniquely owned test schema.
            Base.metadata.create_all(engine)
            with Session(engine) as db:
                for device in ('desktop','mobile'):
                    c=Complaint(gmail_message_id=uuid4().hex,gmail_thread_id=uuid4().hex,
                        sender_email='customer@example.test',email_subject=f'E2E {device} giao hàng trễ',
                        email_body='Đơn hàng giao trễ, xin hỗ trợ kiểm tra.',received_at=now(),
                        is_complaint=True,complaint_type='late_delivery',processing_status='completed')
                    db.add(c);db.flush()
                    db.add(CaseMessage(complaint_id=c.id,gmail_message_id=c.gmail_message_id,
                        gmail_thread_id=c.gmail_thread_id,direction='inbound',sender_email=c.sender_email,
                        subject=c.email_subject,body=c.email_body,occurred_at=now(),processing_status='completed'))
                db.commit()
            print('Isolated synthetic browser workspace ready on 127.0.0.1:8082',flush=True)
            uvicorn.run(app,host='127.0.0.1',port=8082,access_log=False,log_level='warning')
        finally:
            engine.dispose()
            with admin.begin() as connection:
                connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
            admin.dispose()
            print('Removed owned browser test schema and credentials',flush=True)


if __name__=='__main__':
    main()
