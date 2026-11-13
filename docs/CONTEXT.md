# Context — CURRENT và TARGET v3

Khảo sát code: 13/11/2026, Asia/Ho_Chi_Minh. Hackathon 14/11/2026, 07:30–11:30, ba fullstack dùng AI; đủ sáu hạng mục, bắt buộc Cloud Run. Sau đợt docs-only, người dùng đã giao triển khai BASE giới hạn: DB đầy đủ + container + cấu hình Cloud Run, tiếp tục trên ứng dụng hiện có.

## CURRENT có bằng chứng code

| Phần | Entry point | Hiện có |
|---|---|---|
| API | backend/app/main.py | health/status/stats/list/detail/sync/retry |
| DB | backend/app/models.py, schema_v1.py, backfill_v1.py | 13 bảng/203 cột, migration0005; local PostgreSQL17 đã nâng cấp và giữ dữ liệu cũ |
| Pipeline | backend/app/services/sync.py | lưu email trước AI, extraction/verification/policy/retry/dedupe |
| Gmail | backend/app/services/gmail.py | raw MIME, readonly, phân trang; chưa lưu thread/ảnh |
| AI | backend/app/services/ai.py, gemini.py, groq_service.py | provider explicit, schema validation |
| Policy | backend/app/services/policy.py | chỉ late-delivery shipping-refund, guard delivered cần refactor |
| Frontend | frontend/src/App.tsx, api.ts, types.ts | list/filter/detail/sync/retry; chưa login/workflow/send/ảnh |
| Local | Dockerfile, docker-compose.app.yml, infra/ | React/FastAPI một URL8080 + PostgreSQL17; cloud scripts chưa thực thi tạo tài nguyên |

## Kiểm chứng BASE ngày 14/11/2026

- Trước thay đổi: 62 backend tests đạt. Sau BASE: 92 tests đạt trên PostgreSQL17; upgrade mới/cũ, backfill lặp và Alembic check đạt.
- Backup custom-format mode0600 trong backend/.secrets/backups; migration thử trên database khôi phục trước khi nâng local0004→0005. Fingerprint toàn cột cũ của3 orders/7 complaints không đổi.
- Docker build thành công bằng Node22/Python3.11; smoke GET UI/assets/API/DB/404 đạt; container tạm không AI/Gmail key vẫn boot/health và tôn trọng PORT9090.
- Project claimpilot-513010 ACTIVE; preflight báo billing chưa hoạt động. Chỉ có script/config cloud, chưa Cloud SQL/Run/Secrets/Storage/Scheduler thật.
- Chưa auth, Principal/CaseStore/harness, module shells hoặc workflow v3; pipeline cũ vẫn ghi projection legacy. A/B/C phải nối messages/runs/version/audit bằng nghiệp vụ mới; schema có sẵn không tự thực hiện luồng.
- 78 test FS, live Google và ALL1 chưa được nghiệm thu. Chi tiết hiện hành trong [IMPLEMENTATION_REPORT](../IMPLEMENTATION_REPORT.md).

## Lịch sử khảo sát trước BASE

- Build frontend đạt; backend 31 passed/31 setup errors do không kết nối PostgreSQL trong phiên khảo sát, không toàn suite xanh.
- Có gcloud CLI; chưa xác minh project/billing/IAM; chưa xác nhận DB current migration, Playwright/live Google/cloud trong đợt docs.
- IMPLEMENTATION_REPORT ghi Groq từng xử lý email lưu sẵn thành công, Gemini từng timeout. Chưa probe lại; đây không phải kết quả live mới.
- HEAD khảo sát 64bc6d2, dirty README/models/Gemini/Groq/tests/App và migration0004 chưa commit. Kiểm tra lại trước code, không reset/commit hộ.

## TARGET v3 thay thiết kế draft-only

Một hồ sơ nhiều email → AI hoặc manual → xác minh/policy/ảnh → nhiều vòng decision/resolution → preview/edit → nhân viên Gửi hoặc Lưu nháp → chờ khách/thực hiện ngoài app → resolved/close; inbound sau đóng mở lại. Send không chạy do AI/Scheduler, không payment API.

Luồng/enum chuẩn [WORKFLOW](WORKFLOW.md), schema [DATABASE](DATABASE_DESIGN.md), wire [API](API_SPECIFICATION.md), UI [UI_UX](UI_UX_SPECIFICATION.md). Code hiện tại là điểm xuất phát, được mở rộng/refactor theo sản phẩm; không freeze những thiếu sót của code vào yêu cầu.

## Phạm vi

Một doanh nghiệp/Gmail/staff account và một đơn/hồ sơ, dữ liệu mẫu. Không multi-tenant/payment/kho/video/push/split-merge UI. Role A/B/C là developers, không ba nhân viên trong app. Tính năng mới vẫn TARGET cho tới AC01–AC12 có bằng chứng.

## Bắt đầu

Database đã chốt **FROZEN_SPEC CLAIMPILOT_MVP_DB_V1**,13 bảng/203 cột tại DATABASE_DESIGN, có DB01–DB12 và quy tắc không tự ALTER sau BASE. Schema đã thành metadata/migration0005 và chạy local. Chỉ DB01/DB02/DB04 đã có evidence local; các gate nghiệp vụ/live/cloud còn thiếu, không suy ra từ 92 tests.

Đọc AGENTS → context này → WORKFLOW → SHARED_CONTRACTS → TASK → task fullstack cá nhân. Đợt BASE đã chạy schema local/container; chưa cloud hoặc gửi thư. Xem CHANGELOG để biết thay đổi thiết kế; kiểm tra TASK để biết thực thi thật.

## Phân công v3 hiện hành

A tự làm UI/API/DB/tests workspace/auth/intake/status và nền Cloud Run; B tự assessment/manual/text/policy/ảnh/GCS; C tự quyết định/composer/Gmail draft-send/lifecycle. Không còn A toàn backend/B toàn frontend/C toàn Google-cloud. [Shared contracts](SHARED_CONTRACTS.md) chốt BASE/ports/module owner/harness để ba người bắt đầu song song. Registry/migration aggregate A tích hợp, model/schema/business B/C tự viết theo frozen design.

12 task FS + BASE/ALL1 trong TASK; 78 tests đã chuyển owner/ID; dòng “Mã cũ” trong mỗi test giữ thông tin đối chiếu, mốc MERGE/RELEASE. Không task slide/thuyết trình; dữ liệu mẫu tối thiểu chỉ fixture. BASE DB/container đã có; harness/domain deployment và tính năng FS còn phải làm.
