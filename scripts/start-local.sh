#!/usr/bin/env bash
# Explicit developer launcher; app startup never changes the SQL schema.
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"
if [[ ! -x backend/.venv/bin/python ]]; then
  echo 'Create backend/.venv and install backend/requirements.lock.txt first.' >&2
  exit 1
fi
docker-compose up -d db
cd backend
CURRENT_REVISION="$(.venv/bin/alembic current 2>/dev/null)"
if [[ "$CURRENT_REVISION" != '0006 (head)' ]]; then
  .venv/bin/python -m scripts.verify_local_upgrade --apply-local
fi
.venv/bin/python -m scripts.setup_local
cd ../frontend
if [[ ! -d node_modules ]]; then npm ci; fi
npm run build
cd ../backend
echo 'Open http://localhost:8080 — local username/password are in backend/.secrets/local-access.json'
exec .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8080 --no-access-log
