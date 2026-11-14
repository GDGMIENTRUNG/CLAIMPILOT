# C — fullstack Resolution, Source-aware Reply và Safety v4

Nguồn [requirements](../AI_CUSTOMER_SUPPORT_REQUIREMENTS.md), [TASK](../TASK.md), [contracts](../SHARED_CONTRACTS.md). Đọc AGENTS/CONTEXT/WORKFLOW/DATABASE/API/UI/security/errors/testing. Lần này docs-only, không chạy Gmail mutation.

## Bốn task
- FS-C1: Staff approve/reject/request_information, resolution/note/missing fields, assessment snapshot/version/audit và history nhiều vòng; AI chỉ đề xuất.
- FS-C2: AI/manual composer dùng permitted facts/eligible KB sources và pinned business settings; safety_quality role/check endpoint + QualityPanel/citations; edit/save/preview giữ input, nguồn thiếu/mâu thuẫn/stale có manual/rewrite path, không bypass check.
- FS-C3: Gmail draft/confirmed send/reserve/complete/idempotency/unknown/reconcile. Reserve revalidate case/reply/decision/latest inbound + passed check/content/source/settings/preview token. Network ngoài transaction; completion sent+outbound+audit atomic; source đổi không replay side effect.
- FS-C4: Manual fulfillment/resolved/close/reopen và history; dữ liệu cũ/sent bodies giữ nguyên khi KB/settings thay đổi; tích hợp full-loop và đo thời gian thao tác pilot.

## Ownership và dependency
C resolution/reply/safety frontend/backend; A shared auth/CaseStore/settings/client factory và B KB retrieval/resolve. Dùng immutable CaseContext/SettingsSnapshot/SourceRef; test/dev doubles khi dependency chưa có. C tự reserve/complete/checks; A append outbound join cùng UoW, không commit riêng.
Existing ComplaintDecision/CaseReply/ReplyOperation/case lifecycle dùng nguyên mappings. reply_checks/run refs là CR-001 PROPOSED; chưa duyệt thì BLOCKED_CR, không sửa0005/nhét JSON keys hoặc dựng check passed giả.

## Safety và bàn giao
Không tự gửi do AI/Scheduler/approve, không payment hoặc giả fulfillment; scope Gmail compose phải kiểm task C, không suy từ API key. Coding agent live send cần task/mailbox controlled rõ ràng, sản phẩm cần staff preview/confirmed send. Unknown không auto resend; idempotency replay trả persisted result trước freshness check.
[32 tests C](../test-cases/C_TEST_CASES.md); code/DB/browser/mock/live/cloud tách evidence, không tự VERIFIED hoặc commit/push/spawn/reset. Gửi UI/router/quality/port/env/deps/test variants/blocker và việc cần A/B tích hợp.
