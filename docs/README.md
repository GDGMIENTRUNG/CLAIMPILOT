# ClaimPilot — SDD v3 cho ba fullstack

[Đọc tổng quan dự án, chức năng, flow và nhiệm vụ ba người trong một file](../TONG_QUAN_CLAIMPILOT.md).

**Bắt đầu:** [AGENTS](../AGENTS.md) → [CONTEXT](CONTEXT.md) → [WORKFLOW](WORKFLOW.md) → [SHARED_CONTRACTS](SHARED_CONTRACTS.md) → [TASK](TASK.md) → task cá nhân. [AI_PROMPTS](AI_PROMPTS.md) có prompt khởi động/tiếp tục/ghép/review.

## Ai làm gì

- [A Workspace + Cloud Run](tasks/A_WORKSPACE.md): auth/intake/queues/conversation/status + platform; tự UI/API/DB/tests.
- [B Assessment + Evidence](tasks/B_ASSESSMENT.md): verification/manual/text/policy/ảnh/GCS; tự UI/API/DB/tests.
- [C Resolution + Communication](tasks/C_RESOLUTION.md): decisions/composer/Gmail send-draft/lifecycle; tự UI/API/DB/tests.
- [Timeline](IMPLEMENTATION_PLAN.md): contract-first, ghép sớm, không chờ một người làm toàn backend. Cloud Run bắt buộc; không task thuyết trình.

## Sản phẩm/hợp đồng/chất lượng

- [PRD](PRD.md), [SRS](SRS.md), [WORKFLOW](WORKFLOW.md), [architecture](SYSTEM_ARCHITECTURE.md).
- [Shared ports/file owner](SHARED_CONTRACTS.md), [database](DATABASE_DESIGN.md), [API](API_SPECIFICATION.md), [UI/UX](UI_UX_SPECIFICATION.md), [sáu features](FEATURE_SPECIFICATION.md).
- [Coding](CODING_CONVENTIONS.md), [errors](ERROR_HANDLING.md), [security](SECURITY.md), [deployment Cloud Run](DEPLOYMENT.md).
- [Testing](TESTING_GUIDELINES.md); test fullstack [A32](test-cases/A_TEST_CASES.md), [B19](test-cases/B_TEST_CASES.md), [C27](test-cases/C_TEST_CASES.md); thông tin đối chiếu mã cũ nằm trong từng case.
- [AC01–AC12](ACCEPTANCE_MATRIX.md), [release checklist](RELEASE_CHECKLIST.md), [decisions](DECISIONS.md), [known issues](KNOWN_ISSUES.md), [changelog](CHANGELOG.md).

CURRENT là code; TARGET là thiết kế; VERIFIED cần bằng chứng. Docs v3 thay cách phân tầng cũ, giữ workflow nhiều email/decision và nhân viên xác nhận gửi. Các test vẫn NOT_RUN, FS tasks vẫn TODO; module/harness/Cloud Run mới chưa được code trong đợt sửa tài liệu. [README gốc](../README.md) giữ hướng dẫn chạy CURRENT.
