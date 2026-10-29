# ClaimPilot

A local staff workspace for the first 30% milestone: Gmail → Gemini → PostgreSQL order verification → deterministic policy assessment → React dashboard. Gmail is the sole intake channel. The app never sends replies, approves refunds, or performs transactions.

## Architecture

- `backend/app`: FastAPI routes and Pydantic contracts; SQLAlchemy models; Gmail, Gemini, synchronization, and policy services.
- `backend/migrations`: versioned Alembic schema. `backend/scripts`: Gmail authorization and repeatable fictional order seeding.
- `frontend/src`: React/TypeScript dashboard, filters, pagination, and complaint detail drawer. Email content is rendered as escaped text.
- PostgreSQL 17 runs through Compose with persistent storage and a loopback-only port.

The original email is committed before AI processing. A unique Gmail message ID prevents duplicates, including concurrent insertion attempts. Failed analyses stay visible as `processing_failed`. With `GMAIL_RETRY_FAILED=true`, saved failures are retried even outside the current query; with `false`, only failures matching the current query can be retried. Malformed/unreadable Gmail messages are reported individually without aborting the batch. An unreadable message cannot become a complaint until it can be parsed.

AI output is validated and is never used as proof of order existence or delivery. The detail API and UI distinguish extracted identifiers from the linked database order. A sender/customer email mismatch requires staff verification. Order details are read from the linked database row; verification status and policy assessments capture the last processing run. Later database changes do not automatically reprocess a successful case and can leave its assessment out of date.

## Prerequisites

Python 3.11+ (verified here with 3.14), Node 22.12+, npm, and Docker with Compose. On macOS with Colima, start it using `colima start`. Either `docker compose` or the standalone `docker-compose` command works; the examples below use the latter.

## Local setup

From the repository root:

```sh
cp .env.example .env
cp backend/.env.example backend/.env
```

Choose a local PostgreSQL password. Set `POSTGRES_PASSWORD` in root `.env` and the same password in backend `DATABASE_URL` (URL-encode reserved characters). Local environment files and OAuth tokens are ignored by Git. If these files were already generated during development, preserve them rather than copying over them.

```sh
docker-compose up -d db
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt
cd backend
.venv/bin/alembic upgrade head
.venv/bin/python -m scripts.seed_data
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

In another terminal, from the repository root:

```sh
npm --prefix frontend ci
npm --prefix frontend run dev
```

Open **http://localhost:5173**. API docs: **http://127.0.0.1:8000/docs**. Vite proxies `/api` to FastAPI. For a separate frontend host, set `VITE_API_BASE_URL` in `frontend/.env` and set the exact `FRONTEND_ORIGIN` in `backend/.env`; restart both servers. Backend settings resolve `.env` relative to `backend/`, independent of shell location.

Stop the servers with Ctrl-C; stop PostgreSQL with `docker-compose stop db`. Do not remove the database volume unless you intend to erase stored cases.

## Google Cloud and Gmail OAuth

1. Create/select a controlled Google Cloud project and enable **Gmail API**.
2. Configure Google Auth Platform branding, audience, and data access. For external testing, add the designated Gmail test account as a test user. Add the read-only scope `https://www.googleapis.com/auth/gmail.readonly`.
3. Create an OAuth client of type **Desktop app**. Copy its client ID and secret to backend `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`; never commit downloaded credentials.
4. Leave `GOOGLE_REDIRECT_URI=http://localhost:8080/` for the local loopback callback. This implementation uses installed-app authorization, not a web-server OAuth client.
5. Run from `backend/`:

```sh
.venv/bin/python -m scripts.authorize_gmail
```

Authorize only the controlled Gmail account in the browser. The command saves a refresh token to `backend/.secrets/gmail-token.json` with owner-only permissions. The read-only scope allows reading and searching, not sending or modifying messages. Refresh happens on sync. If consent is revoked or the token expires, rerun the command; testing-mode refresh tokens may expire according to Google's OAuth rules.

No account password or access token belongs in `.env`. The token file contains credentials and must remain private. Configuration status only checks presence of the token and API key; actual validity is checked during sync.

Set `GMAIL_QUERY` to select likely complaints. Default: inbox messages within 30 days containing complaint/refund/damage/delay terms. Set `GMAIL_BATCH_SIZE` between 1 and 100 (the example configuration uses 10). Sync is manual and synchronous. When enabled, saved retries and new messages share one batch limit. The reader scans past already saved emails (up to 1,000 IDs per sync) to drain older matching messages without reanalyzing them. For larger inboxes, narrow the query by date. The default query is keyword-based, so staff should tune it for their test emails and language.

## Gemini

Create a Gemini API key for the controlled project/account and set `GEMINI_API_KEY` in backend `.env`. Set `GEMINI_MODEL` to a model available to that account supporting structured output (example: `gemini-2.5-flash`). Restart FastAPI after changing configuration.

Subject and up to 60,000 body characters are sent to Gemini. Original email text stays in PostgreSQL. Only use fictional complaints and a controlled account for this milestone. Missing credentials, invalid output, quota errors, and provider failures are reported without fabricated analysis. Retry saved failures using Sync Emails after correcting setup.

SDK references: [official Google Gen AI Python SDK](https://googleapis.github.io/python-genai/) and [Gmail Python message API](https://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.users.messages.html).

## Seed data and policies

Seeding is safe to repeat and preserves existing orders:

| Order | Customer | Expected | Actual | Shipping fee |
| --- | --- | --- | --- | --- |
| DH001 | dh001@example.com | 2026-10-25 | 2026-10-27 | 40,000 VND |
| DH002 | dh002@example.com | 2026-10-25 | 2026-10-25 | 20,000 VND |
| DH003 | dh003@example.com | 2026-10-29 | Not delivered | 30,000 VND |

Dates and delivery status come exclusively from PostgreSQL. A delivered late order with a shipping-fee refund request is eligible **for staff review**, subject to sender matching. On-time delivery does not qualify under this sample policy. Missing dates/identifiers, unconfirmed delivery, unsupported requests, or sender mismatch require information/review. Unknown identifiers return `order_not_found`.

To demonstrate an eligible case with a real Gmail sender, intentionally update DH001's `customer_email` in your local test database to the controlled sender's address. Do not change real customer records. This also allows testing sender mismatches separately.

Case statuses: successful assessments enter `pending_review`; insufficient information enters `insufficient_information`; provider/validation failures enter `processing_failed`. `processed` is reserved for explicitly completed records; there is no status-editing workflow in this milestone. Its dashboard count can correctly remain zero. Statistics are global; list filters do not alter overview totals.

## API

| Method and route | Result |
| --- | --- |
| GET `/api/health` | Database connectivity; 503 when unavailable |
| GET `/api/integrations/status` | Credential-presence flags, without secrets |
| POST `/api/gmail/sync` | `successful`, `skipped`, `failed`, and per-message error categories |
| GET `/api/complaints` | Paginated items/total; `page`, `page_size`, `case_status`, `complaint_type` |
| GET `/api/complaints/{id}` | Original email, AI analysis, linked order, assessment, status |
| GET `/api/dashboard/stats` | Database-backed total, pending review, insufficient information, processed |

404 indicates a missing complaint; 422 invalid query inputs; 409 an overlapping sync; 503 database/provider setup or connectivity failure. Partial batches return 200 with explicit failure counts. The single-process lock is not a distributed queue. Run one worker. CORS allows only the configured frontend origin. This unauthenticated local MVP must remain bound to loopback; it is not a public deployment.

## Tests

```sh
cd backend
.venv/bin/pytest -q
cd ../frontend
npm run build
```

`backend/requirements.lock.txt` records the exact Python packages used in verification; `frontend/package-lock.json` locks frontend dependencies.

Backend tests use real PostgreSQL, creating a random schema per test and dropping only that schema on cleanup. The database user needs schema-creation permission. Optionally set `TEST_DATABASE_URL` to a dedicated PostgreSQL database; otherwise tests use the configured database with isolated schemas. External Google calls are mocked in automated tests. They do not verify live Gmail or Gemini.

Frontend browser checks are documented with their setup in `frontend/e2e/`; run with the backend and Vite already running. Use `npm --prefix frontend exec -- playwright install chromium` once if needed, then run `npm --prefix frontend run test:e2e`.

## Manual live integration procedure

1. Start PostgreSQL, migrate, seed, configure Gemini, authorize Gmail, and start both apps.
2. Set DH001's customer email to the controlled sender address for the eligible-case demonstration.
3. Send a new test email to the authorized Gmail inbox: subject `Complaint: DH001 late delivery`; body explaining late delivery and requesting the shipping fee refund. Ensure it matches `GMAIL_QUERY`.
4. Click Sync Emails. Confirm the actual Gmail message is saved, Gemini returns an email-specific summary, DH001 is linked, database dates are shown separately, and the assessment is `eligible_for_review`.
5. Sync again. Confirm no duplicate record exists and the email is counted as skipped.
6. Send a complaint with no order identifier and another with `UNKNOWN999`. Confirm missing/unknown outcomes and readable explanations.
7. Test an on-time order, undelivered order, and sender mismatch. Verify none becomes an eligible late-delivery shipping refund.
8. With a fresh eligible email, temporarily remove the Gemini key and restart the backend. Sync: the email must remain visible as failed. Restore the key/restart/resync and verify that the same record is successfully analyzed.
9. Check browser details: original body is plain text, AI information is labelled, database information is labelled, and no refund/email was sent.

Record the actual outcomes in `IMPLEMENTATION_REPORT.md`. A rendered dashboard or mocked test does not satisfy the live demonstration requirement.

## Limitations

Manual bounded sync, one Gmail account, one process, local token file, simple complaint keyword filtering, and the sample policy only. No live shipping lookup, payment integration, replies, authentication, status editing, queue, multi-tenancy, or automatic financial actions. See the implementation report for verified results and outstanding live setup.

## Current local test mode

The local backend `.env` is configured for at most **10 matching emails per sync**, using `in:inbox newer_than:7d subject:"CLAIMPILOT TEST"`. Send test emails with `[CLAIMPILOT TEST]` in their subject. Gmail search matches that phrase; it does not require it to be the first characters. The three previously failed emails remain stored but are not retried outside this query (`GMAIL_RETRY_FAILED=false`).

`GEMINI_TIMEOUT_SECONDS=30` bounds each provider request, and automatic SDK retries are disabled. A provider-wide Gemini failure stops the batch early; the `deferred` count means those messages were not attempted and remain available for a later sync. This reduces waiting during an outage; it cannot guarantee successful or instant AI processing. Set `GMAIL_RETRY_FAILED=true` and broaden `GMAIL_QUERY` when ready to leave test mode, then restart FastAPI.

### Retry one saved complaint

Open a failed complaint and choose **Retry Gemini analysis**. `POST /api/complaints/{id}/analyze` reuses the saved email, calls Gemini, verifies the extracted order in PostgreSQL, and evaluates the policy. It does not scan Gmail or require the saved email to match the current test query. A shared lock prevents concurrent sync/analysis; completed analyses return 409 rather than rerunning. Failures remain saved with a specific error. The button displays progress, disables repeated clicks, and refreshes details and statistics after completion. A retry does not bypass provider timeouts or fabricate AI results.

## Temporary Groq provider

The local installation is temporarily configured with `AI_PROVIDER=groq`. Gemini remains implemented and its credentials are preserved. Set these in `backend/.env`:

```env
AI_PROVIDER=groq
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-120b
GROQ_TIMEOUT_SECONDS=20
```

Fill `GROQ_API_KEY` locally with a key created in the Groq console, then restart FastAPI. Never paste the key into chat or commit it. Open a saved failed email and choose **Retry Groq analysis** to test one complaint without scanning Gmail.

The selected model supports strict JSON Schema according to [Groq's structured-output documentation](https://console.groq.com/docs/structured-outputs). The adapter uses low reasoning effort, a bounded response size, a 20-second default request timeout, and no automatic retries. Local Pydantic validation and database order/policy verification still apply. This model choice is intended to balance extraction quality and latency; actual accuracy and response times require live testing with your account and representative fictional complaints. No speed or correctness guarantee is claimed.

Selection is explicit; there is no automatic cross-provider fallback. Original email subject/body will be sent to the selected provider when analysis runs. The dashboard shows the current provider/model and whether its key is present. To switch back, set `AI_PROVIDER=gemini` and restart FastAPI; no database migration or Gmail reauthorization is needed. Existing saved emails remain available for retry.
