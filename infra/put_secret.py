"""Upload a real secret via stdin, never CLI value args or repository files.

Requires backend Python deps + gcloud auth. This script is NOT run by BASE.
"""
import argparse
import getpass
from pathlib import Path
import subprocess
from sqlalchemy.engine import URL

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('secret', choices=['claimpilot-db-runtime', 'claimpilot-db-migrator',
                                    'claimpilot-gemini-key', 'claimpilot-groq-key', 'claimpilot-gmail-token'])
parser.add_argument('--project', default='claimpilot-513010')
parser.add_argument('--file', type=Path, help='Local credential file; content never logged')
parser.add_argument('--sql-connection', help='PROJECT:REGION:INSTANCE; for DB URL secrets only')
args = parser.parse_args()
if args.file:
    value = args.file.read_bytes()
elif args.secret.startswith('claimpilot-db-'):
    if not args.sql_connection:
        parser.error('--sql-connection is required for a database URL')
    role = 'claimpilot_runtime' if args.secret.endswith('runtime') else 'claimpilot_migrator'
    password = getpass.getpass(f'Existing Cloud SQL password for {role}: ')
    if not password:
        parser.error('Empty database password')
    value = URL.create('postgresql+psycopg', username=role, password=password,
                       database='claimpilot', query={'host': '/cloudsql/' + args.sql_connection}).render_as_string(hide_password=False).encode()
else:
    value = getpass.getpass('Secret value (hidden): ').encode()
if not value.strip():
    parser.error('Empty secret; no fake placeholder versions are uploaded')
result = subprocess.run(['gcloud', 'secrets', 'versions', 'add', args.secret,
                         '--project=' + args.project, '--data-file=-', '--format=value(name)'],
                        input=value, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if result.returncode:
    raise SystemExit('Upload failed; check project/IAM/secret existence with gcloud (no secret value printed).')
print('Created secret version:', result.stdout.decode().strip())
