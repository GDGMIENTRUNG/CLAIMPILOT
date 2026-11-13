# Thực thi ba fullstack — v3, 14/11/2026 07:30–11:30

## Đích và phạm vi đợt cập nhật

Xây sản phẩm đúng WORKFLOW và release lên Google Cloud Run. A workspace/cloud, B assessment/evidence, C resolution/communication; mỗi người tự làm UI/API/DB/tests. Không có nhiệm vụ làm slide/thuyết trình/diễn tập. Fixtures và controlled Google checks vẫn cần để chứng minh sản phẩm hoạt động.

Cập nhật14/11: BASE DB13 bảng/203 cột, migration0005/backfill/container/config cloud đã có và kiểm local; chưa auth/CaseStore/Principal/registry/harness, feature v3 hoặc cloud thật. BASE dưới đây chỉ làm phần còn thiếu, không dựng lại ứng dụng/database; xem IMPLEMENTATION_REPORT. Bốn giờ là mục tiêu, không bảo đảm quota/provisioning/merge tự thành công.

## Chuẩn bị BASE trước 07:30

Schema khóa CLAIMPILOT_MVP_DB_V1: đủ13 bảng/203 cột trong DATABASE_DESIGN, dùng cho mốc 50%,80% và toàn MVP. Đầu ra BASE cần models/migration/backfill/fixtures đúng schema + DB01–DB12; models/migration/backfill đã làm và kiểm local0005; còn shared runtime/harness/fixtures hợp đồng và các gate nghiệp vụ/cloud. Sau BASE ba người chỉ viết business/CRUD trên schema, không tự thêm cột theo từng feature. Key/model đổi không đòi SQL.

- Cả ba đọc WORKFLOW/schema/API/UI và SHARED_CONTRACTS; review dirty Git, chốt baseline chung, ba worktree. Không reset/commit hộ.
- A tổng hợp core model fields/registry/CaseStore Protocol/Principal/client factory/migration outline, Cloud Run project/billing/IAM/APIs/SQL provisioning.
- B review assessment/evidence mappings có sẵn, tự chuẩn bị DTO/env/deps, raw MIME/ảnh và order/message factories, probe text + Gemini ảnh/private bucket.
- C review decisions/replies/operations mappings có sẵn, tự chuẩn bị DTO/env/deps, reply factories, OAuth compose quyền draft/send/reconcile.
- Chốt module shells và harness riêng từng domain; không bắt B/C chờ backend A xong. Real implementation ports ghép sau, production không fake.

## Lịch ghép sản phẩm

| Giờ | A fullstack Workspace + Platform | B fullstack Assessment | C fullstack Resolution |
|---|---|---|---|
| 07:30–07:45 | Kiểm core contracts/harness/cloud readiness | Kiểm DTO/schema own + raw/order fixtures | Kiểm DTO/schema own + decision/reply fixtures |
| 07:45–08:45 | Login/queues/intake, Run skeleton, core CaseStore | Manual verification/text/policy UI/API | Decision/history/composer UI/API, send reservation |
| 08:45–09:15 | Ghép registry + deploy URL skeleton; migration aggregate | Nối CaseStore/Principal thật, đánh giá real persisted case | Nối CaseStore/client thật, không chờ B text nếu manual/context fixture |
| 09:15–10:15 | Follow-up/scheduler/status, Cloud SQL/Secrets wiring | GCS/Gemini ảnh và data/version safety | Gmail send/draft/unknown + fulfillment/close |
| 10:15–11:15 | Cả nhóm AC01–AC12 trên Cloud Run, sửa lỗi chặn sản phẩm |
| 11:15–11:30 | Freeze revision cuối, kiểm release/rollback, không thêm tính năng |

Không có thời gian riêng thuyết trình trong task phát triển. Nếu preflight cloud/OAuth/quota thiếu, báo BLOCKED sớm; không thay real integration bằng fake để kịp giờ.

## Dependency theo hợp đồng, không theo người viết backend

Bắt đầu: mỗi phần chỉ cần BASE + test doubles đúng DTO; auth thật/Google/CaseStore chưa sẵn không chặn viết UI→API→DB phần mình. Hợp đồng chốt trước nghiệp vụ, không hai API/schema khác nhau.

Khi ghép: A intake → B.analyze_message/ingest_message, B/C mutations → A.CaseStore, C completion → A.append_message outbound. Không có A business → B business → C business tuần tự. C tự implement reserve/complete, B tự implement evidence/Storage/text, A tự implement sync/cloud/auth.

A tổng hợp Alembic/deps/settings từ manifests B/C, không viết thay router/model/component domain. B/C test metadata ở schema thử độc lập; release dùng aggregate migration một head. Seed kiểm thử: A tạo orders/messages cần cho intake, B attach ảnh/assessment, C factories decision/reply chỉ trong test; không fixture sent giả trên Cloud Run release.

## Kiểm tra và change-control

Mỗi task kiểm MERGE trước ghép; RELEASE và AC01–AC12 trước phát hành. Dùng lại evidence cùng revision khi đủ quan sát, tránh gửi nhiều thư thật không cần thiết. Reviewer xác nhận thực tế, không chỉ số pass.

Thay shared contract có quyết định ghi lại, delta schema/wire/fixtures và owner A tích hợp composition; domain owner đồng ý phần ảnh hưởng. Không tạo thêm microservice/DB riêng để né merge. Nguồn phân công hiện hành TASK FS-*; mã cũ được ghi ngay trong từng test case để đối chiếu khi cần.
