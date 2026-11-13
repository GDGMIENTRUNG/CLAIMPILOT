# ClaimPilot — AI Coding theo ba phần fullstack (SDD v3)

## Đọc trước khi thực hiện

1. [CONTEXT](docs/CONTEXT.md) → [WORKFLOW](docs/WORKFLOW.md) → [TASK](docs/TASK.md).
2. [SHARED_CONTRACTS](docs/SHARED_CONTRACTS.md) và [timeline](docs/IMPLEMENTATION_PLAN.md).
3. Task fullstack [A Workspace](docs/tasks/A_WORKSPACE.md), [B Assessment](docs/tasks/B_ASSESSMENT.md) hoặc [C Resolution](docs/tasks/C_RESOLUTION.md).
4. [Database](docs/DATABASE_DESIGN.md), [API](docs/API_SPECIFICATION.md), [UI/UX](docs/UI_UX_SPECIFICATION.md), [features](docs/FEATURE_SPECIFICATION.md).
5. [Testing](docs/TESTING_GUIDELINES.md), test đúng vai trò [A](docs/test-cases/A_TEST_CASES.md)/[B](docs/test-cases/B_TEST_CASES.md)/[C](docs/test-cases/C_TEST_CASES.md), [security](docs/SECURITY.md)/[errors](docs/ERROR_HANDLING.md).

## Mục tiêu và nguồn sự thật

- A/B/C đều fullstack: tự làm UI, API, persistence và tests trong phần sản phẩm. Không dùng lại cách chia A toàn backend/B toàn frontend/C toàn Google-cloud.
- A: workspace/intake/auth + nền Cloud Run. B: assessment/verification/policy/evidence. C: decisions/replies/send/fulfillment/close.
- Sản phẩm bắt buộc chạy một URL Google Cloud Run, cùng origin React/FastAPI, Cloud SQL, private Storage, Secret Manager, Scheduler. Không tách ba microservice để chia việc.
- Yêu cầu sản phẩm là đích; code hiện có là CURRENT, được refactor/mở rộng. Không reset/ghi đè công việc người khác. Không đổi stack hoặc thêm multi-tenant ngoài yêu cầu.
- WORKFLOW định nghĩa trạng thái, DATABASE_DESIGN định nghĩa schema, API_SPECIFICATION định nghĩa wire, SHARED_CONTRACTS định nghĩa interface/file owner, TASK định nghĩa việc hiện hành. Mâu thuẫn phải giải quyết và báo người phụ thuộc trước đổi contract.
- Schema chuẩn là **CLAIMPILOT_MVP_DB_V1 / FROZEN_SPEC** trong DATABASE_DESIGN: 13 bảng, dùng chung cho mốc 50%,80% và MVP. BASE triển khai đủ models/migration một lần; sau đó A/B/C không tự thêm/đổi bảng/cột/index/enum hay migration head. Chỉ đổi schema sau yêu cầu có bằng chứng và thống nhất nhóm; đổi key/model AI không cần đổi SQL. FROZEN_SPEC chưa có nghĩa đã migrate/pass DB gates.
- Chỉ mã FS-A1..FS-A4, FS-B1..FS-B4, FS-C1..FS-C4 là task cá nhân hiện hành. BASE là chuẩn bị chung, ALL1 là nghiệm thu chung; mã cũ chỉ dùng đối chiếu ở dòng “Mã cũ” trong từng test case, không dùng để giao việc mới.

## Làm song song và tích hợp

- Ba worktree từ cùng baseline BASE; mỗi phần có router/models/schemas/services/components/tests riêng. A chỉ sở hữu composition root, core CaseStore và infra; không là người viết backend cho B/C.
- Mỗi người ánh xạ model/DTO phần mình đúng dictionary đã khóa; B/C review metadata trước khi A tổng hợp baseline13 bảng và một migration chain. Sau BASE chỉ CRUD/business theo schema, không tự tạo schema delta lúc code feature. B/C vẫn dùng harness để phát triển mà không chờ A code nghiệp vụ/runtime.
- B/C dùng contract harness và test doubles cho dependency chưa có. Chỉ tests/development được giả, config production cấm fake adapters hoặc bỏ qua auth để app trông thành công.
- Cross-domain case mutation qua CaseStore transaction/version/audit. Không sửa thẳng bảng domain người khác hoặc mở transaction lồng gây mất atomicity.
- Entry files App/main/models/config/API helper được chuẩn bị interface trong BASE; domain chỉ sửa module của mình. Thay đổi shared gửi owner A tích hợp, API nghiệp vụ B/C tự sở hữu.
- Không tự spawn agent; mỗi phiên nhận một role. Không tự commit hộ, reset/clean, sửa migration đã áp dụng hoặc xóa dữ liệu.

## Quyền và phạm vi

- Nhân viên preview rồi confirmed send; không send từ AI/approve/Scheduler. Coding agent không tự gửi thư thật chỉ vì có API: live test cần task và mailbox nhóm kiểm soát.
- Không payment/refund API, không secrets/PII trong prompt/log/Git/frontend. Email/ảnh không đáng tin, không URL fetch tùy ý.
- Lần cập nhật SDD v3 hiện tại chỉ docs: không feature code/migration/cloud/send. Đây không phải lệnh cấm code về sau khi người dùng giao FS task.

## Bàn giao và review

Task/owner; commit/revision; file; API/schema/env/deps delta; test IDs/biến thể + thực tế; loại mock/DB/browser/live/cloud; blocker; người nhận/reviewer. Test MERGE trước ghép, RELEASE trước nghiệm thu. NOT_RUN/FAIL/BLOCKED không là PASS; owner đề nghị REVIEW, reviewer xác nhận VERIFIED theo TESTING_GUIDELINES. ALL1 cần full-loop trên Cloud Run; không thay live bằng fixture. Không giao việc làm slide/thuyết trình như feature task.
