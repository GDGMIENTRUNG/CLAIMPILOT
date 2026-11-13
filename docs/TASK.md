# Task board — ba phần fullstack v3

A/B/C đều làm UI + API + dữ liệu + tests. Cloud Run là đích bắt buộc; không phân tầng theo công nghệ. Toàn bộ task feature vẫn TODO. Không giao slide/thuyết trình/diễn tập như việc xây sản phẩm. Dữ liệu mẫu tối thiểu là fixture kiểm thử, không một vai trò demo riêng.

[BASE và interfaces](SHARED_CONTRACTS.md) được chốt chung trước phát triển song song; không chờ A hoàn thiện nghiệp vụ. Mã cũ chỉ đối chiếu ở dòng “Mã cũ” trong từng test case, không còn là task được giao.

Database đã chốt đặc tả **CLAIMPILOT_MVP_DB_V1: 13 bảng** tại [DATABASE_DESIGN](DATABASE_DESIGN.md). BASE phải ánh xạ đủ schema/migration/fixtures và kiểm DB01–DB12 trước khóa baseline runtime; các gate hiện NOT_RUN. Sau BASE, FS tasks chỉ CRUD/business/UI trên schema này, không tự thêm bảng/cột khi lên mốc 50%/80%. Điều này không đánh dấu BASE hoặc feature đã xong.

| ID | Owner | Đầu ra fullstack | Cần khi bắt đầu / lúc ghép | AC | Test | Status |
|---|---|---|---|---|---|---|
| BASE | A+B+C, A tổng hợp | Frozen schema/DTO, module shells, registry/harness, fixture hợp đồng | Git baseline review; không chờ feature | contracts + migration checks | bộ test theo từng owner | TODO |
| FS-A1 | A | Auth/session/CSRF + LoginPage + shared api client | BASE; B/C dùng Principal stub lúc đầu | AC10 | [FS-A1](test-cases/A_TEST_CASES.md#fs-a1) | TODO |
| FS-A2 | A | Gmail read/thread/dedupe, queues/conversation/technical queue, fixtures intake | BASE; gọi B assessment/evidence port qua doubles rồi real | AC02/07 | [FS-A2](test-cases/A_TEST_CASES.md#fs-a2) | TODO |
| FS-A3 | A | Image/Cloud Run/SQL/Secrets, registry/core CaseStore, migration aggregate, health frontend/API | BASE; B/C schema/env manifests để aggregate lúc ghép | AC12 | [FS-A3](test-cases/A_TEST_CASES.md#fs-a3) | TODO |
| FS-A4 | A | Scheduler/OIDC/DB sync lock/cursor, SyncStatus UI, last_success/deferred và tests | BASE; wiring ports B lúc ghép | AC10/12 | [FS-A4](test-cases/A_TEST_CASES.md#fs-a4) | TODO |
| FS-B1 | B | Order verification/manual correction/ownership, API + AssessmentPanel | BASE + CaseStore/Principal double | AC03/04 | [FS-B1](test-cases/B_TEST_CASES.md#fs-b1) | TODO |
| FS-B2 | B | Text AI + năm policy/version/missing fields, result UI và tests | BASE + synthetic message/CaseContext | AC04/11 | [FS-B2](test-cases/B_TEST_CASES.md#fs-b2) | TODO |
| FS-B3 | B | MIME image ingestion/private GCS/Gemini one-two-side, API + EvidencePanel | BASE + raw MIME fixture/message factory; intake thật khi ghép | AC02/09 | [FS-B3](test-cases/B_TEST_CASES.md#fs-b3) | TODO |
| FS-B4 | B | Assessment snapshot/manual-vs-AI/version safety, UI warnings, domain coverage/fixtures | BASE; FS-B1..FS-B3 triển khai cùng domain | AC04/06/11 | [FS-B4](test-cases/B_TEST_CASES.md#fs-b4) | TODO |
| FS-C1 | C | Decisions/resolution/history UI + API/DB transactions nhiều vòng | BASE + context/ownership double | AC01/02/06 | [FS-C1](test-cases/C_TEST_CASES.md#fs-c1) | TODO |
| FS-C2 | C | AI/manual composer/edit/save/preview/stale-context UI + API | BASE + own decision factory/text provider double | AC04/05/06 | [FS-C2](test-cases/C_TEST_CASES.md#fs-c2) | TODO |
| FS-C3 | C | Gmail draft/confirmed send/reconcile/idempotency + composer trạng thái và reserve/complete | BASE + fake client/CaseStore, OAuth thật khi nghiệm thu | AC01/05/06/08/10 | [FS-C3](test-cases/C_TEST_CASES.md#fs-c3) | TODO |
| FS-C4 | C | Fulfillment ngoài app/resolved/close/reopen, UI timeline + tests | BASE + own sent-result factory; A inbound primitive khi ghép | AC01/07 | [FS-C4](test-cases/C_TEST_CASES.md#fs-c4) | TODO |
| ALL1 | A+B+C | Full acceptance/release trên Cloud Run, không mocks production | cả ba phần ghép, real credentials | AC01–AC12 | [matrix](ACCEPTANCE_MATRIX.md) | TODO |

## Bàn giao và trạng thái

TODO → IN_PROGRESS → REVIEW → VERIFIED; BLOCKED có nguyên nhân/người gỡ. Owner giao cả UI/API/models/tests và manifests shared cần tích hợp; reviewer đối chiếu test IDs/biến thể/evidence trước VERIFIED. MERGE và RELEASE đều bắt buộc theo mốc; PASS phần riêng không tự làm ALL1 PASS.

| Task | Commit/revision | Test IDs + thực tế | Mock/DB/browser/live/cloud | Owner/reviewer/blocker |
|---|---|---|---|---|
| — | — | Chưa thực hiện tính năng trong lần sửa docs | — | — |

Không chờ task khác VERIFIED mới viết feature mình: dùng frozen contract/doubles trước; chỉ đánh dấu phần live còn thiếu đúng trạng thái. Không cộng số pass để che một test bắt buộc FAIL/BLOCKED/NOT_RUN. [Testing](TESTING_GUIDELINES.md), [prompt](AI_PROMPTS.md), [timeline](IMPLEMENTATION_PLAN.md).
