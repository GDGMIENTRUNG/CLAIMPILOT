# A — fullstack Workspace, Settings và Platform v4

Nguồn [requirements](../AI_CUSTOMER_SUPPORT_REQUIREMENTS.md), [TASK](../TASK.md), [contracts](../SHARED_CONTRACTS.md). Đọc AGENTS/CONTEXT/WORKFLOW/DATABASE/API/UI/security/testing trước code. Lần hiện tại chỉ docs, chưa giao thực thi feature.

## Bốn task
- FS-A1: Login/session/CSRF/Origin/rate-limit và shared API client; bảo vệ mọi API cả KB/settings/agent progress, 401 giữ route không replay mutation.
- FS-A2:5-tab navigation/Tổng quan/Hộp thư/Dữ liệu, keyword search + processing/workflow filters, conversation/history và Gmail intake/canonical/thread/dedupe/parse failures; fixtures orders tương đối, không demo role.
- FS-A3: Core CaseStore/UoW/Principal/GoogleClientFactory/registry/composition và Cloud Run/SQL/Secrets; business settings và agent settings fullstack, immutable versions/validation/409, guardrails mandatory. Aggregate CR-001 sau review, không sửa0005.
- FS-A4: OIDC/Scheduler/advisory lock/5 inbound/20 threads/240s/cursor/deferred; coordinator persisted runs/steps và progress UI/API, dispatch B/C ports, failure/review/manual path; không gửi thư từ pipeline.

## Ownership và dependency
A workspace/settings/shared/infra; B owns KB/retrieval/assessment/evidence và C owns writer/safety/send. A compose KnowledgePanel/AssessmentPanel/EvidencePanel/ResolutionPanel/QualityPanel từ exports, không viết domain thay họ. Core append_message join transaction C để sent/outbound/audit atomic.
13 mappings đã có; phần settings/run storage BLOCKED_CR cho tới CR-001 được review và giao migrate riêng. Contracts/harness/core/auth/UI độc lập vẫn làm được; doubles chỉ test/dev.

## Bắt đầu và bàn giao
Kiểm Git/code, source và actual DB head, không reset; một role/worktree, không tự spawn/commit/push. Tạo/publish interfaces trước, cùng baseline với B/C, báo manifests cần ghép. Thiếu runtime B/C ghi rõ phần chưa nối, production không fake.
[38 test A](../test-cases/A_TEST_CASES.md): MERGE và RELEASE từng biến thể. Cloud preflight chỉ kiểm trạng thái khi chưa có task provision; billing/credit cũ không chứng minh đã active. Feature chỉ REVIEW khi code/tests/evidence đủ, reviewer khác mới VERIFIED.
