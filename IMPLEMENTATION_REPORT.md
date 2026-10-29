# ClaimPilot — 30% MVP implementation report

Verified on October 28, 2026 (Asia/Ho_Chi_Minh).

The implementation is ready for local Google credential setup. **The full milestone is not yet complete:** no controlled Gmail OAuth credentials/token or Gemini API key were supplied, so actual complaint retrieval and live Gemini analysis have not been demonstrated.

## Implemented

- PostgreSQL models, JSONB extraction fields, unique Gmail ID protection, delivery/order constraints and indexes, Alembic migration, and idempotent fictional-order seed script.
- Read-only Gmail installed-app OAuth command, refresh-token handling, bounded query/pagination, nested MIME and Unicode decoding, HTML-to-text conversion, individual message error handling, and database deduplication.
- Official Gemini SDK calls with configured model, structured Pydantic validation, error categories, persisted failed emails, and manual retries without fabricated analysis.
- Database order verification, sender matching, deterministic policy explanations, and recommendations requiring human review.
- Documented REST API, exact-origin CORS, sanitized database/provider errors, sync counts, and a single-process sync lock.
- Responsive React staff dashboard with database statistics, filters/pagination, original email, labelled AI extraction, verified order information, policy assessment, loading/empty/error states, and actual sync feedback.
- Setup instructions, environment examples, dependency locks, automated tests, and manual live integration procedure.

## Important files

| Component | Files |
| --- | --- |
| Database | `backend/app/models.py`, `backend/migrations/versions/0001_initial.py`, `backend/scripts/seed_data.py` |
| Pipeline | `backend/app/services/gmail.py`, `gemini.py`, `sync.py`, `policy.py` |
| API and configuration | `backend/app/main.py`, `schemas.py`, `config.py`, `backend/.env.example` |
| OAuth | `backend/scripts/authorize_gmail.py` |
| Dashboard | `frontend/src/App.tsx`, `api.ts`, `types.ts`, `style.css` |
| Verification | `backend/tests/`, `frontend/e2e/`, `frontend/playwright.config.ts` |
| Setup | `README.md`, `docker-compose.yml`, `.env.example`, `.gitignore` |

## Actual verification results

| Check | Result |
| --- | --- |
| PostgreSQL startup/readiness | Passed: PostgreSQL 17 container running |
| `alembic upgrade head` | Passed: initial schema applied |
| Seed script, twice | Passed: exactly three orders remain |
| `alembic check` | Passed: no ORM/migration differences |
| `pytest -q` | **33 passed**, using real PostgreSQL and isolated per-test schemas |
| FastAPI startup | Passed on `127.0.0.1:8000` |
| `/api/health` | Actual HTTP 200 with `status: ok` |
| Dashboard stats through Vite proxy | Actual HTTP 200; initial database contains zero complaints |
| Integration status | Actual response reports Gmail/Gemini unconfigured |
| Missing Gmail authorization sync | Actual HTTP 503 and useful UI error; no fabricated success |
| `npm run test:e2e` | **6 passed**: desktop and mobile |
| `npm run build` | Passed: TypeScript check and Vite production build |
| Desktop/mobile screenshots | Inspected; populated mobile overflow issue fixed and regression assertion added |
| npm dependency audit during install | Zero reported vulnerabilities |
| Live Gmail OAuth/retrieval | **Blocked: client credentials and user authorization required** |
| Live Gemini analysis | **Blocked: API key required** |

Backend tests cover all eight requested cases, plus sender mismatch, missing order dates, unsupported requests, repeated seeding, database uniqueness, saved-email retry outside the query, partial sync failures, MIME/Unicode/HTML decoding, pagination past saved messages, API detail/filter/error contracts, sanitized database failures, CORS, overlapping syncs, SDK request wiring, and rate-limit handling. Google calls are mocked in these tests; PostgreSQL is real.

The browser suite verifies real backend/proxy connectivity, the initial empty workspace, and the missing-authorization response. Populated-detail and error-recovery scenarios use explicitly intercepted API fixtures and verify safe rendering, filters, keyboard dismissal, and mobile containment. They are not evidence of live Google functionality.

Two backend dependency deprecation warnings remain: Starlette's current HTTPX test-client compatibility path and a Google SDK typing alias on Python 3.14. They did not fail tests. Playwright also emits environment color-setting warnings. Initial sandbox network denials and browser-detected filter/mobile issues were resolved before the final passing runs.

## Run and configure

PostgreSQL, FastAPI, and Vite were left running for review:

- Dashboard: http://localhost:5173
- API documentation: http://127.0.0.1:8000/docs

For later restarts, run from the project root:

```sh
docker-compose up -d db
```

Backend terminal:

```sh
cd backend
.venv/bin/alembic upgrade head
.venv/bin/python -m scripts.seed_data
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend terminal:

```sh
cd frontend
npm run dev
```

A generated local database password is stored only in ignored, owner-readable root/backend `.env` files. No Google secrets or tokens were generated. For a fresh installation, follow README prerequisites and dependency-install commands.

To enable the live pipeline, configure the Desktop app OAuth client and Gemini key in `backend/.env`, run `.venv/bin/python -m scripts.authorize_gmail` from `backend/`, restart FastAPI, and follow the README manual integration procedure. For an eligible live DH001 case, set the fictional order's customer email to the controlled sender address first; otherwise sender mismatch correctly blocks eligibility.

## Definition of Done

“Completed” below means implemented and verified as described; mocked provider tests are identified explicitly. Live demonstration remains outstanding.

| # | Requirement | Status | Evidence / remaining work |
| --- | --- | --- | --- |
| 1 | PostgreSQL runs and schema exists | Completed | Running container and applied Alembic migration |
| 2 | Sample orders can be seeded | Completed | Seed executed twice; three orders remain |
| 3 | FastAPI starts | Completed | Running server and actual health response |
| 4 | React starts and communicates with FastAPI | Completed | Vite proxy and real-backend browser checks |
| 5 | Gmail OAuth and retrieval implemented | Completed; live verification blocked | Official client implementation and parser/pagination tests; authorization still required |
| 6 | Gemini analyzes actual retrieved content with credentials | Blocked | SDK implementation verified with mocks; actual Gmail/Gemini credentials absent |
| 7 | Backend validates AI output | Completed | Structured schema and malformed-output tests |
| 8 | Extracted order verified in PostgreSQL | Completed | Real PostgreSQL policy/pipeline/API tests; Google mocked |
| 9 | Deterministic policy result | Completed | Late/on-time/undelivered/missing/unknown/mismatch tests |
| 10 | Complaint stored in PostgreSQL | Completed | Real database pipeline/API tests with mocked intake/AI |
| 11 | Dashboard shows original, AI, order, and policy data | Completed; live case pending | PostgreSQL API tests plus browser fixtures; no live Google case yet |
| 12 | Repeated synchronization avoids duplicates | Completed | Sync-repeat test and database unique-constraint test |
| 13 | Missing/unknown order IDs handled | Completed | PostgreSQL policy tests and readable reasons |
| 14 | Core automated tests pass | Completed | 33 backend and 6 browser tests passed |
| 15 | README supports setup and operation | Completed | Local migration/seed/start/test commands exercised; Google steps require account setup |
| 16 | Report identifies live verification gaps | Completed | This report distinguishes real local checks, mocked providers, and blocked live checks |

## Known limitations

No known unresolved failure in the exercised local workflow. Live Google integration correctness remains unverified until credentials are supplied. This is a single-account, single-process, local staff MVP without authentication or case-status editing. Run only on loopback. Gmail filtering is keyword-based; sync scans at most 1,000 matching IDs, processes up to the configured new-message batch, and retries up to 25 saved failures per invocation. AI receives at most the first 60,000 email-body characters. Failed/unreadable Gmail fetches are reported and retried on later syncs if still matched; unreadable messages cannot yet be stored as parsed complaints.

Only the sample shipping-refund policy is implemented. Sender matching is a review safeguard, not proof of identity. Linked order details reflect the current database row, while verification status and policy results capture the last processing run. Those assessments can become stale after database edits; successful cases are not automatically reanalyzed. The `processed` count remains zero until records are explicitly marked completed outside this milestone. No refunds or customer emails are executed.

## Follow-up: live credential troubleshooting

The user subsequently configured Google credentials and completed Gmail consent. A real sync retrieved and preserved three emails, but Gemini processing failed. Initial live diagnosis found a Gemini HTTP 400 caused by `additional_properties` in `generation_config.response_schema`. The integration now sends `response_json_schema=Analysis.model_json_schema()`, retaining strict local Pydantic validation. The backend was restarted with this change.

The configured model `gemini-3.8-flash` is recognized by the live model metadata endpoint and advertises `generateContent`. However, structured fictional-complaint requests returned HTTP 504, including after increasing the timeout from 45 to 90 seconds. A separate minimal request asking only for `OK`, without a response schema, also returned HTTP 504. Therefore live complaint analysis is still unverified and currently blocked by generation timeouts. A diagnostic probe of the earlier example model `gemini-2.5-flash` returned HTTP 404 indicating it is unavailable for this account; the user's configured model was preserved.

Gemini errors now distinguish invalid requests, invalid keys, access denial, missing models, rate limits, and provider timeouts instead of displaying only `Gemini Unavailable`. Regression tests were updated for JSON Schema and expanded for those categories: **38 backend tests passed**. The failed emails remain stored for manual retry. No new live sync was performed after these probes, and no successful live Gemini analysis is claimed. No API keys, OAuth tokens, or customer email bodies were printed during diagnosis.

## Follow-up: bounded test-email synchronization

At inspection, PostgreSQL contained **three processing_failed complaints and no successfully analyzed complaints**. The user's local configuration now selects only inbox emails from the last seven days containing `CLAIMPILOT TEST` in the subject, with a shared maximum of ten attempted messages per sync. Saved failures outside the query are temporarily excluded (`GMAIL_RETRY_FAILED=false`); no existing emails or complaints were deleted. Broader intake and out-of-query retries can be restored through configuration.

Gemini calls now use a configurable 30-second timeout and one SDK attempt. Provider-wide failures stop processing the remaining batch instead of repeating the same failed request for every email; the API/UI show remaining unattempted messages as `deferred`. Invalid analysis of an individual message still permits subsequent messages to proceed. Verification after these changes: **41 backend tests passed**, and TypeScript/Vite production build passed. No new live complaint analysis success is claimed.

## Follow-up: processing status accuracy

The newest saved complaint ultimately reported `gemini_timeout_retry_sync`; four saved complaints now have failed analysis. A separate UI/state defect was corrected: newly persisted emails now use `processing` while awaiting Gemini, instead of prematurely appearing failed. Migration `0002` expands the status constraint and handles old records without an error; interrupted processing can be retried when selected by the configured intake/retry settings. Verification: migration applied, no Alembic drift, **42 backend tests passed**, frontend production build passed. The Gemini timeout remains unresolved; no successful analysis is claimed.

## Follow-up: retry a selected saved email

Added `POST /api/complaints/{id}/analyze` and the **Retry Gemini analysis** button in complaint details. The shared analysis service reuses the saved email, commits `processing`, calls Gemini, verifies the order, and evaluates the policy; provider failures are persisted. It never initializes Gmail or creates a second complaint. The sync/analysis lock rejects overlapping calls, and completed analyses cannot be accidentally rerun. Keyboard focus handling now includes the new action.

Verification: **45 PostgreSQL-backed backend tests passed**, including saved-email retries without Gmail, timeout persistence, completed-case protection, and concurrency rejection. **8 fixture-based desktop/mobile browser tests passed**, including progress, disabled repeated clicks, success refresh, error recovery, and keyboard access. Production frontend build passed. The backend was restarted with the new route.

Additional synthetic live probes still failed: low-thinking `generateContent` returned HTTP 504; the official Interactions API also timed out. No production change to the provider endpoint/model was made based on those unsuccessful probes. One attempt to retry saved test complaint #5 through the new local endpoint returned HTTP 409 because a synchronization/analysis was already in progress; no second concurrent Gemini call was started. Live AI complaint processing remains unverified; email content and credentials were not printed.

## Follow-up: temporary Groq provider

At the user's request, added the official Groq SDK adapter and explicit `AI_PROVIDER=gemini|groq` selection. The local environment selects Groq temporarily, with an empty `GROQ_API_KEY` placeholder and `GROQ_MODEL=openai/gpt-oss-120b`. Gemini implementation/credentials are preserved, and there is no silent provider fallback.

Groq requests use strict JSON Schema, low reasoning effort, a 20-second configurable timeout, 2,048 completion-token limit, and zero automatic retries. All output still passes through Pydantic and the same database verification/policy services. Provider errors are sanitized and stop a batch when appropriate. Dashboard configuration and retry labels show the active provider/model.

Verification: **60 backend tests passed** using PostgreSQL and mocked external APIs; **10 fixture-based desktop/mobile browser tests passed**; production build passed. Dependency lock updated. No live Groq calls were made because the user intends to enter the key later. Model selection is based on Groq's documented strict structured-output support; actual latency and extraction quality have not yet been measured. Add the key locally, restart FastAPI, and test a saved complaint.

## Follow-up: successful live Groq verification

After the user entered a Groq key locally, a real `openai/gpt-oss-120b` call analyzed a fictional late-delivery complaint successfully in approximately **0.7 seconds**, extracting DH001, `late_delivery`, and `shipping_fee_refund`. The backend was restarted to load the key.

A real call to `POST /api/complaints/5/analyze` then processed the existing controlled test email successfully with HTTP 200 in approximately **1.2 seconds**. It extracted DH001, verified the linked PostgreSQL order as delivered, and persisted `insufficient_information` because the sender does not match the fictional order customer email. This is an expected ownership-review safeguard, not an AI processing failure. No Gmail rescan, refund, outgoing email, or customer-email change occurred. No key or email-body content was printed.

Live Groq analysis of one stored Gmail test complaint and the AI → PostgreSQL → policy → persisted API result are now verified. These individual timings are observations, not latency or accuracy guarantees. Live Gemini generation remains unverified due to the earlier failures. A fresh live Gmail sync using Groq and a matching-customer eligible case have not yet been demonstrated.
