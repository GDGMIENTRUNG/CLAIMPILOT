# Changelog

## 2026-11-14 — BASE DB và container trên ứng dụng hiện có

- Thêm schema snapshot13 bảng/203 cột,13 ORM mappings, migration0005 và repeat-safe legacy backfill; giữ IDs/body/tri-state/timestamps, không sửa migration0001–0004.
- Backup trước thay đổi; thử clone và fresh database trước khi nâng local lên0005. Alembic check không drift; fingerprint3 orders/7 complaints giữ nguyên.
- Thêm Docker Node22/Python3.11, SPA/API cùng origin, compose app8080, read-only OAuth refresh; .env/token cũ giữ nguyên và không đóng vào image.
- Thêm cấu hình/scripts Cloud Run, private bucket/SQL/secrets/IAM/migration Job và grants tách runtime/migrator. Chỉ chuẩn bị; preflight project claimpilot-513010 ACTIVE, billing chưa hoạt động; không tạo tài nguyên cloud.
- Regression62 trước/92 sau đều PASS;92 tests cũng đạt trong image Python3.11. Container HTTP/DB/boot không key và Chrome desktop/mobile đạt. Test FS/live/cloud chưa nghiệm thu. BASE vẫn IN_PROGRESS vì chưa harness/Principal/CaseStore/registry/module shells; không triển khai feature A/B/C trong đợt này.
- Không gửi mail/call AI thật, không commit/push tự động. Xem IMPLEMENTATION_REPORT cho evidence và giới hạn.

## 2026-11-13 — khóa đặc tả database MVP

- Chốt CLAIMPILOT_MVP_DB_V1 / FROZEN_SPEC:13 bảng/203 cột, dictionary type/null/default, enum, composite FK, unique/partial index và checks.
- Bổ sung text_analysis_runs/gmail_intake_failures, canonical alias và fulfillment/closure metadata; explicit confirmed operation snapshot, sent outbound FK, private GCS generation/size/dimensions.
- Chốt cấu trúc JSON, transaction/version/idempotency, backfill dữ liệu cũ, DB01–DB12 và không ALTER riêng sau BASE. Các mốc 50%/80% dùng cùng baseline.
- Đồng bộ API projections/technical failure read, task A/B/C/shared contracts, hướng dẫn AI/testing và overview; giữ78 test NOT_RUN, FS tasks TODO.
- Chỉ sửa tài liệu, chưa tạo models/migration/scaffold, chưa migrate database hoặc deploy cloud trong đợt này.
- Kiểm tra tĩnh dictionary: đủ13 bảng/203 cột,19 khai báo FK và 6 partial unique được dựng/compile qua SQLAlchemy PostgreSQL dialect trong script tạm, giữ tên cột ORM legacy. Đây không phải chạy DDL/DB01–DB12; database gates vẫn NOT_RUN.

## 2026-11-13 — dọn tài liệu chuyển tiếp

- Xóa ba file task phân tầng cũ A_BACKEND/B_FRONTEND/C_INTEGRATIONS_CLOUD và DEMO_RUNBOOK đã chỉ còn trỏ sang tài liệu hiện hành.
- Xóa bảng TEST_CASE_MIGRATION riêng vì từng test đã có FS-ID, owner và dòng “Mã cũ”; giữ đủ 78 cases và thông tin đối chiếu tại chỗ.
- Cập nhật các liên kết/hướng dẫn đọc để chỉ dùng task fullstack và release checklist hiện hành. Bản ghi các đợt trước bên dưới là lịch sử.
- Không đổi yêu cầu sản phẩm, task/tiêu chí/test outcome hoặc code ứng dụng.


## 2026-11-13 — SDD v3: ba phần fullstack, Cloud Run bắt buộc

- Thay phân tầng cũ bằng 12 FS tasks: A Workspace/Platform, B Assessment/Evidence, C Resolution/Communication; từng người tự UI/API/persistence/tests.
- Thêm SHARED_CONTRACTS cho BASE schema/registry/ports/CaseStore/credential factory/harness, để bắt đầu song song không chờ A business runtime.
- Giữ schema/wire/workflow đã chốt, cập nhật owner module/model/API/UI và migration/dependency aggregation; Cloud Run một image/cùng origin, A platform/B GCS-Gemini/C Gmail write.
- Chuyển đủ 78 test sang FS IDs: A 32/B 19/C 27, thêm TEST_CASE_MIGRATION đối chiếu từng ID; giữ NOT_RUN và task TODO. Mốc kiểm tra đổi sang RELEASE.
- Bỏ task slide/thuyết trình/diễn tập, chuyển kiểm chứng sản phẩm sang RELEASE_CHECKLIST; giữ fixtures tối thiểu và AC01–AC12.
- Các task docs cũ và DEMO_RUNBOOK chỉ redirect, không còn chỉ dẫn thực thi phân tầng. Bản ghi bên dưới là lịch sử, không nguồn phân công hiện hành.
- Chỉ cập nhật docs: chưa scaffold/code/harness/migration/cloud/send trong đợt này.
- Kiểm tra: 37 Markdown liên kết hợp lệ, đủ 12 FS tasks/78 test IDs và ánh xạ một-một từ bộ cũ, sáu features đủ 11 mục, acceptance vẫn NOT_RUN. Hash 43 file ứng dụng không đổi; không có mã task phân tầng cũ trong chỉ dẫn hiện hành.


## 2026-11-13 — test case theo nhiệm vụ và review độc lập

- Thêm ba tài liệu test case: A 28, B 23, C 27; tổng 78 cases cho đủ 18 task A0–A5/B0–B5/C0–C5, có dữ liệu/bước/kỳ vọng/loại bằng chứng/mốc MERGE hoặc DEMO.
- Gắn link test vào TASK và DoD từng người, AGENTS, AI_PROMPTS, index/README; thêm prompt cho phiên reviewer độc lập.
- Bổ sung fixture chung, completion gate, mẫu báo cáo theo ID/biến thể và phân biệt unit/DB/browser/Google/cloud.
- Tất cả cases khởi tạo NOT_RUN, task feature giữ TODO và acceptance giữ NOT_RUN. Chỉ bổ sung docs; không thực thi feature tests, gửi email, migrate hoặc deploy.
- Kiểm tra tài liệu đạt: 31 Markdown, 78 test IDs duy nhất, đủ trường/traceability/mốc MERGE–DEMO, link từ 18 task hợp lệ; giữ trạng thái TODO/NOT_RUN. So hash 43 file ứng dụng không đổi; không dùng kết quả kiểm tra tài liệu làm bằng chứng feature pass.

## 2026-11-13 — SDD v2 theo luồng doanh nghiệp

- Chỉnh bộ docs thống nhất theo hồ sơ nhiều email, nhiều quyết định, manual review và theo dõi đến đóng/mở lại.
- Thay draft-only bằng preview/edit/confirmed send trong app; lưu Gmail Draft là lựa chọn phụ. Cấm auto-send theo AI/Scheduler, không cấm tính năng nhân viên bấm gửi.
- Chốt database đích/ERD/backfill và API/version/idempotency/unknown, cùng UI conversation/composer/fulfillment.
- Thêm WORKFLOW làm nguồn state machine và ACCEPTANCE_MATRIX AC01–AC12; cập nhật sáu features đủ 11 thành phần.
- Cập nhật task/prompt/timeline A/B/C, security/error/deploy/testing/demo và nguồn Google chính thức.
- Cho phép mở rộng/refactor theo yêu cầu và change-control, bỏ giới hạn một quyết định hoặc giữ modal cũ bằng mọi giá.
- Chỉ sửa tài liệu: không code tính năng, chạy migration, tạo cloud hoặc gửi mail. Mọi task feature vẫn TODO, AC vẫn NOT_RUN.
- Kiểm tra bộ docs: 28 Markdown (gồm AGENTS/README gốc), links/fences hợp lệ; sáu features mỗi feature đủ 11 mục; AC01–AC12 và task A/B/C 0–5 đầy đủ. So hash 43 file ứng dụng baseline không đổi. Đây là kiểm tra tài liệu, không phải nghiệm thu tính năng.

## 2026-11-13 — bộ docs ban đầu (được v2 thay thế ở phần TARGET)

- Thêm PRD/SRS/architecture/database/API/features/UI/security/deploy và hướng dẫn AI/task/demo.
- TARGET ban đầu draft-only, một quyết định; các giới hạn đó không còn là yêu cầu hiện hành.
- Baseline code lịch sử: frontend build đạt, backend 31 passed/31 DB setup errors; không phải kết quả feature mới.
