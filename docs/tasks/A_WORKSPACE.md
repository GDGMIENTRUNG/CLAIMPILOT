# A — fullstack Workspace và Cloud Run

## Prompt copy cho AI

> Đọc AGENTS → CONTEXT → WORKFLOW → SHARED_CONTRACTS → TASK → task này; đọc API/DATABASE/UI_UX/SECURITY/TESTING và bộ A_TEST_CASES. Bạn làm FS-A1..FS-A4, cả UI/API/persistence/tests cho workspace/auth/intake/status và nền Google Cloud Run. Đây không phải vai trò viết toàn backend cho B/C. Chuẩn bị composition root/CaseStore/Principal/GoogleClientFactory theo BASE, để B/C dùng contract doubles khi implementation của bạn chưa xong. Giữ dữ liệu và dirty Git. Tự triển khai login/queues/conversation/Gmail read/sync/Scheduler; ghép B AssessmentPanel và C ResolutionPanel qua interface, không sửa nội bộ domain họ. Cloud Run cùng-origin/SQL/Secrets, production không mock. Không tự gửi mail từ intake/scheduler, không payment. Bàn giao feature có UI/API/tests và evidence MERGE/RELEASE, không giao việc demo/thuyết trình.

## Việc được giao

- **FS-A1:** LoginPage + auth router/sessions/CSRF/rate-limit + shared api client; CurrentStaff Protocol ở BASE để B/C test router độc lập, production dependency thật.
- **FS-A2:** queues/CaseList/ConversationPanel và API/messages/canonical thread/dedupe; Gmail read + parser text/metadata. Gọi ports B sau saved message, follow-up không keyword vẫn cập nhật, outbound C gửi không tạo complaint mới. Tạo fixture orders/messages tối thiểu, không nhiệm vụ trình diễn.
- **FS-A3:** composition registry, core CaseStore UoW/version/audit, metadata facade và Alembic aggregate, Docker/Cloud Run/Cloud SQL/Secrets/health UI/API. B/C tự viết model/service/router/component, bạn chỉ tổng hợp shared manifests. Không ép chờ migration production để code domain tests.
- **FS-A4:** Scheduler OIDC/DB lock/bounded cursor/retry/deferred + SyncStatus/last_success UI, kiểm tests sync/status/cloud. Nền cloud đúng project, không để public internal route bỏ verify OIDC.

## File owner và interface

Database khóa là CLAIMPILOT_MVP_DB_V1: A tổng hợp đủ13 bảng trong BASE, kiểm DB01–DB12, chưa pass thì không báo DB sẵn sàng. A sở hữu thêm gmail_intake_failures và canonical aliases; không tạo hồ sơ giả khi parse lỗi. B/C ánh xạ metadata đúng dictionary, sau BASE không gửi schema delta bất ngờ khi làm feature. Không tự ALTER/DROP hoặc migration head mới trong FS task.

Backend module workspace và shared primitives/composition, frontend feature workspace/shared shell; cloud artifacts/settings/lock/migration aggregate do A tích hợp. Legacy main/App/models/config/api helper là điểm tích hợp một owner, domain B/C không sửa cạnh tranh. Chốt imports/feature slots trong BASE.

A append inbound/audit/version/reopen trong core UoW không cần gọi service lifecycle C mới lưu được thư. A không implement policy/ảnh/send thay B/C; dùng B.analyze_message/B.ingest_message, C append outbound dùng A primitive. Shared Google factory quản token, read-only mount refresh memory; Gmail write module do C.

## Bắt đầu độc lập

Dùng text/evidence ports double chỉ test/dev, kiểm workspace với own DB/schema fixture. Khi ghép đổi real B ports; B/C dùng fake CaseStore trong domain harness, không chờ bạn xong login hoặc CaseStore runtime. Không chạy fake adapters trên Cloud Run release.

## DoD

[Tests A](../test-cases/A_TEST_CASES.md) đủ MERGE/RELEASE; contract tests core/migration đúng; API/UI workspace thật trên Run, Scheduler thật. Bàn giao commit/revision/schema/env/deps/evidence + reviewer. Toàn sản phẩm còn ALL1 với B/C; một URL health200 chưa nghĩa đủ workflow.
