"""Secure backup + restore-on-clone verification before a local additive upgrade."""
import argparse,hashlib,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
from uuid import uuid4
from sqlalchemy import create_engine,inspect,text
from sqlalchemy.engine import make_url
from app.config import settings,ROOT

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--apply-local',action='store_true');args=parser.parse_args()
    repo=ROOT.parent;docker=['docker-compose','exec','-T','db']
    backup=ROOT/'.secrets/backups'/('before_ai_first_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.dump')
    backup.parent.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(backup.parent,0o700)
    with os.fdopen(os.open(backup,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600),'wb') as stream:
        subprocess.run(docker+['pg_dump','-U','claimpilot','-d','claimpilot','-Fc'],cwd=repo,stdout=stream,check=True)
    name='claimpilot_verify_'+uuid4().hex
    subprocess.run(docker+['createdb','-U','claimpilot',name],cwd=repo,check=True)
    original=create_engine(settings.database_url)
    with original.connect() as conn:
        columns={t:[c['name'] for c in inspect(conn).get_columns(t)] for t in ('orders','complaints')}
    def fingerprint(engine):
        with engine.connect() as conn:
            return {t:hashlib.sha256(repr(conn.execute(text('SELECT '+','.join(cols)+' FROM '+t+' ORDER BY id')).all()).encode()).hexdigest() for t,cols in columns.items()}
    before=fingerprint(original)
    clone=create_engine(make_url(settings.database_url).set(database=name))
    try:
        with backup.open('rb') as stream:subprocess.run(docker+['pg_restore','-U','claimpilot','-d',name,'--no-owner','--exit-on-error'],cwd=repo,stdin=stream,check=True)
        env=dict(os.environ,DATABASE_URL=clone.url.render_as_string(hide_password=False))
        cli=str(ROOT/'.venv/bin/alembic')
        for command in (['upgrade','head'],['upgrade','head'],['check']):subprocess.run([cli,*command],cwd=ROOT,env=env,check=True)
        assert fingerprint(clone)==before,'Legacy data changed on clone'
        with clone.connect() as conn:assert len(inspect(conn).get_table_names())==21
        print('Verified clone:20 business tables, one head, repeated upgrade, no drift, all legacy columns preserved.')
        if args.apply_local:
            subprocess.run([cli,'upgrade','head'],cwd=ROOT,check=True)
            assert fingerprint(original)==before,'Legacy data changed locally'
            subprocess.run([cli,'check'],cwd=ROOT,check=True)
            print('Local upgraded; legacy data preserved. Backup:',backup)
    finally:
        clone.dispose();original.dispose()
        subprocess.run(docker+['dropdb','-U','claimpilot',name],cwd=repo,check=True)
if __name__=='__main__':main()
