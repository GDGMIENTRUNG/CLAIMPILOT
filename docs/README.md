# ClaimPilot — Bản đồ tài liệu AI-first v4

Bắt đầu: [AGENTS](../AGENTS.md) → [nguồn yêu cầu REQ-001–032](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md) → [CONTEXT](CONTEXT.md) → [WORKFLOW](WORKFLOW.md) → [TASK](TASK.md) → task cá nhân.
Tên file nguồn thực tế là AI_CUSTOMER_SUPPORT_REQUIREMENTS.md; không tạo bản sao theo tên gõ thiếu.

- Sản phẩm: [PRD](PRD.md), [SRS traceability](SRS.md), [features](FEATURE_SPECIFICATION.md), [UI/UX](UI_UX_SPECIFICATION.md), [overview](../TONG_QUAN_CLAIMPILOT.md).
- Kỹ thuật: [architecture](SYSTEM_ARCHITECTURE.md), [database và CR-001](DATABASE_DESIGN.md), [API](API_SPECIFICATION.md), [shared contracts](SHARED_CONTRACTS.md).
- Thực hiện: [plan](IMPLEMENTATION_PLAN.md), [A](tasks/A_WORKSPACE.md), [B](tasks/B_ASSESSMENT.md), [C](tasks/C_RESOLUTION.md), [prompts](AI_PROMPTS.md).
- Chất lượng: [tests](TESTING_GUIDELINES.md), [A38](test-cases/A_TEST_CASES.md), [B26](test-cases/B_TEST_CASES.md), [C32](test-cases/C_TEST_CASES.md), [AC01–18](ACCEPTANCE_MATRIX.md), [release](RELEASE_CHECKLIST.md).
- Vận hành: [security](SECURITY.md), [errors](ERROR_HANDLING.md), [coding](CODING_CONVENTIONS.md), [deployment](DEPLOYMENT.md), [decisions](DECISIONS.md), [known issues](KNOWN_ISSUES.md), [changelog](CHANGELOG.md).

CURRENT: baseline13 bảng/203 cột, migration0005,92 tests lịch sử và container cơ bản; chi tiết [IMPLEMENTATION_REPORT](../IMPLEMENTATION_REPORT.md).
TARGET:5 mục workspace, KB có duyệt/version,6 vai trò agent, settings, source-aware replies/safety và human confirmed send.
CR-001 đề xuất7 bảng mới; chưa được migrate/review như schema phát hành.96 test đặc tả NOT_RUN. Lần này chỉ viết docs; không triển khai tính năng hoặc tự commit/push.
