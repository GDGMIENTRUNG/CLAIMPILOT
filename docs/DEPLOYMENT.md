# Deployment — TARGET v3, A nền tảng + B/C domain checks

Đây là hướng dẫn task triển khai tương lai, không tuyên bố đã có tài nguyên. Đợt sửa docs không deploy/migrate/gửi email. A làm nền Cloud Run/SQL/Secrets/Scheduler, B cấu hình GCS/Gemini và C xác minh Gmail draft/send; cả ba fullstack, không giao toàn Google/cloud cho C. Region mặc định asia-southeast1, project nhóm có billing. Ghi project/region/URL/image digest/revision/SQL connection name vào bàn giao, không secrets.

## 1. Preflight trước buổi

```sh
gcloud auth list --filter=status:ACTIVE
gcloud config get-value project
gcloud services list --enabled
```
Xác minh đúng project/account/billing, quyền tạo Run/SQL/Storage/Scheduler/Secrets/Artifact Registry/Build và actAs service accounts. Bật APIs tương ứng, Gmail API và OAuth test users. Không tự đổi project khi thiếu quyền.

Consent readonly + compose cho Gmail intake/draft/send; token readonly cũ không đủ. Probe model text và Gemini ảnh bằng dữ liệu giả, ghi model khả dụng thật. Live send chỉ mailbox nhóm kiểm soát, sau click preview xác nhận; Scheduler chỉ sync.

## 2. Tài nguyên và IAM

- Artifact Registry claimpilot; Cloud SQL PostgreSQL 17 instance claimpilot-db, DB/user claimpilot, cấu hình nhỏ được project hỗ trợ, không HA cho MVP. Chuẩn bị provisioning trước khung 4h nếu đã vào task triển khai.
- Bucket private tên theo project, uniform access + public access prevention. Runtime SA chỉ quyền object bucket này, Cloud SQL Client và Secret Accessor trên từng secret. Không Editor/Owner.
- Scheduler SA claimpilot-scheduler riêng; OIDC audience PUBLIC_BASE_URL, email allowlist tại app. Public ingress cho login nên app phải verify token, IAM invoker đơn thuần không bảo vệ route public.
- Secrets: DATABASE_URL, Gemini/Groq keys, Gmail token JSON, password hash; client secret trong token/Secret riêng. Không plain CLI arg/log, frontend hoặc Docker build args.
- SQL qua Run SQL attachment/Unix socket `/cloudsql/PROJECT:REGION:INSTANCE`, psycopg URL password encode đúng; không authorized network 0.0.0.0/0.

## 3. Image/env

Multi-stage Node 22 build → Python 3.11 runtime locked deps, `.dockerignore` loại .env/.secrets/.git/node_modules/venv/artifacts. Bind 0.0.0.0:$PORT default 8080, một worker. SPA dùng /api relative; API routes trước fallback.

| Env TARGET | Giá trị/ý nghĩa |
|---|---|
| DATABASE_URL | Secret, SQL Unix socket |
| AI_PROVIDER | gemini hoặc groq explicit, không silent fallback |
| GEMINI_API_KEY / GROQ_API_KEY | Secrets; chỉ key cần dùng |
| GEMINI_MODEL / GROQ_MODEL | model đã probe, không đoán |
| GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET | OAuth local/Secret nếu service cần, không VITE |
| GMAIL_TOKEN_PATH | /secrets/gmail/token.json mounted |
| GMAIL_TOKEN_READ_ONLY | true cloud, refresh memory |
| GMAIL_ACCOUNT_EMAIL | mailbox controlled, nhận diện outbound |
| GMAIL_QUERY | controlled test khi nghiệm thu; chỉ khám phá thread mới |
| GMAIL_BATCH_SIZE | 5 inbound tối đa/lượt |
| PUBLIC_BASE_URL / FRONTEND_ORIGIN | URL Run canonical cùng origin |
| SESSION_COOKIE_SECURE | true cloud, false chỉ loopback dev |
| STAFF_USERNAME / STAFF_PASSWORD_HASH | account cấu hình, hash Argon2id trong Secret |
| GCS_BUCKET | private bucket |
| SCHEDULER_SERVICE_ACCOUNT | OIDC allowlist email |
| POLICY_CONFIG_PATH | file demo-v2 trong image |
| DEMO_DATE / DEMO_CUSTOMER_EMAIL | 2026-11-14 / địa chỉ nhóm; chỉ seed job cần |

A tích hợp config/env/dependency manifests từ B assessment và C resolution; mỗi domain tự làm provider/service/UI của mình. Secret versions pin cho revision release, không đổi latest ngoài ý muốn. Session TTL 8h; known thread cap20 và sync budget240s là hằng config MVP theo kiến trúc, A/B/C cùng thống nhất.

## 4. Deploy theo thứ tự

Database baseline phát hành phải khớp CLAIMPILOT_MVP_DB_V1 (13 bảng), DB01–DB12 và metadata ba domain đã review; không deploy thiếu bảng B/C rồi ALTER lẻ trong startup. Một migration job có quyền DDL; runtime dùng quyền DML giới hạn, không DDL. Secrets/mode provider do cấu hình, không thêm cột khi nhận key ban tổ chức.

1. Build/push image theo commit/digest, không dùng latest làm bằng chứng.
2. Run Job cùng image/SA/SQL/secrets chạy alembic upgrade head trong backend; đợi exit0, một head. Migration/backfill thử trên old-data fixture trước; không chạy startup mọi instance.
3. Seed CPDEMO bằng Job riêng, upload ảnh giả private; không public seed/reset endpoint. Mail thật không được sinh bởi seed.
4. Deploy service 1CPU/1Gi, timeout300s/concurrency8/max instances1, public login. Business auth + internal OIDC kiểm tra tại app.
5. Lấy canonical URL, update PUBLIC_BASE_URL/FRONTEND_ORIGIN; revision cuối có đúng Origin/audience. Nếu cần skeleton trước migration, chỉ coi health URL bước khởi động, chưa claim acceptance.
6. Scheduler POST /api/internal/gmail/sync, cron */5 * * * *, timezone Asia/Ho_Chi_Minh, OIDC account/audience đúng, deadline300s, max retry1. Sync internal không send email. Cả manual/internal dùng DB lock.
7. Run-now và đợi lượt lịch thật. Kiểm tra last_success/error/deferred và known-thread cursor; reply không keyword vẫn được nhập.

## 5. Smoke/rollback

- Health200; API business anonymous401; internal missing/invalid token401/403; unknown API JSON404, SPA routes hoạt động.
- AC01 gửi controlled sau confirm, AC02 bổ sung ảnh/decision mới, AC05 draft/edit/send, AC09 ảnh Gemini, AC12 Scheduler thật và restart giữ dữ liệu/token/ảnh.
- Reconcile unknown bằng scripts.reconcile_replies, không auto resend. Không bật retry SDK side effect Gmail.
- Ghi revision tốt. Rollback app chỉ khi schema compatible; không giả định binary cũ luôn đọc projection mới an toàn. Pause Scheduler và khóa mutation/gửi trong cửa sổ rollback, không bật hai writer phiên bản khác. Không downgrade/drop DB vội.
- Sau kiểm thử cân nhắc pause lịch và thống nhất việc giữ/xóa tài nguyên; không tự xóa DB/bucket. Kiểm tra chi phí tài nguyên còn chạy.

## Nguồn Google chính thức

- [Cloud Run secrets](https://docs.cloud.google.com/run/docs/configuring/services/secrets).
- [Scheduler/Cloud Run](https://docs.cloud.google.com/run/docs/triggering/using-scheduler): ví dụ service private; app web public này cần thêm verify OIDC ở route.
- [Gmail drafts.send](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.drafts/send) và [messages.send](https://developers.google.com/workspace/gmail/api/reference/rest/v1/users.messages/send): dùng đúng thao tác theo reply, không gọi cả hai cho cùng intent.
- [Gmail threads](https://developers.google.com/workspace/gmail/api/guides/threads): giữ thread/subject/headers.
- [Gmail sync](https://developers.google.com/workspace/gmail/api/guides/sync): MVP chọn bounded polling; History API/push để sau, không claim realtime.

## Task fullstack và release

A FS-A3/FS-A4 quản container/deploy/SQL/Secrets/IAM bindings/Scheduler, B FS-B2/FS-B3 tự probe model và cung cấp GCS/evidence config/deps, C FS-C3 tự consent compose và kiểm Gmail write/reconcile. Migration/job/lock A aggregate metadata B/C theo BASE; không ba migration chain hoặc ba service riêng. B/C vẫn phát triển domain qua harness khi cloud A đang dựng.

[RELEASE_CHECKLIST](RELEASE_CHECKLIST.md) và AC01–AC12 kiểm cả ba UI/API/domain trên một URL. Không có công việc thuyết trình trong deployment backlog. Cloud Run runtime phải bind PORT và image đúng contract: [runtime contract](https://docs.cloud.google.com/run/docs/container-contract), [deploying containers](https://docs.cloud.google.com/run/docs/deploying).
