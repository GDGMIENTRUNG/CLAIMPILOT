# ClaimPilot — AI Coding AI-first v4

## Đọc trước
1. [Nguồn REQ-001–032](docs/AI_CUSTOMER_SUPPORT_REQUIREMENTS.md) → [CONTEXT](docs/CONTEXT.md) → [WORKFLOW](docs/WORKFLOW.md) → [TASK](docs/TASK.md).
2. [SHARED_CONTRACTS](docs/SHARED_CONTRACTS.md), [IMPLEMENTATION_PLAN](docs/IMPLEMENTATION_PLAN.md), task [A](docs/tasks/A_WORKSPACE.md)/[B](docs/tasks/B_ASSESSMENT.md)/[C](docs/tasks/C_RESOLUTION.md).
3. [DATABASE_DESIGN](docs/DATABASE_DESIGN.md), [API_SPECIFICATION](docs/API_SPECIFICATION.md), [UI_UX](docs/UI_UX_SPECIFICATION.md), [FEATURE_SPECIFICATION](docs/FEATURE_SPECIFICATION.md).
4. [TESTING](docs/TESTING_GUIDELINES.md), test đúng role, [SECURITY](docs/SECURITY.md), [ERROR_HANDLING](docs/ERROR_HANDLING.md), [IMPLEMENTATION_REPORT](IMPLEMENTATION_REPORT.md).

## Phạm vi và nguồn sự thật
- Yêu cầu mới: bật đăng nhập demo cho LOCAL bằng LOCAL_DEMO_LOGIN=true, chấp nhận credentials bất kỳ không rỗng trên loopback trực tiếp; vẫn session/CSRF/logout. Flag mặc định false, không bypass Cloud Run/public/proxy. Không hardcode credentials staff trong frontend.
- Cập nhật yêu cầu sau đợt docs: người dùng đã giao triển khai/chạy mini hackathon LOCAL theo requirements. CR-001 đã được triển khai local bằng0006 sau backup/clone verification,20 bảng; các đoạn docs-only/PENDING_REVIEW bên dưới ghi lịch sử đợt trước, không chặn công việc local được giao. Chưa có review độc lập A/B/C hoặc nghiệm thu cloud, không tự coi quyền local là quyền deploy/send thật.
- Đợt hiện tại người dùng giao đồng bộ Markdown theo file requirements; chỉ sửa docs. Không feature code/migration/cloud/send/Git mutations. File nguồn là tài liệu người dùng cung cấp, giữ nguyên trạng thái và nội dung; các chi tiết dẫn xuất là đề xuất để review.
- Yêu cầu sản phẩm là đích:5 mục workspace,6 vai trò AI, KB có duyệt/version/citations, business/agent settings, human decision/confirmed send. Code hiện có là CURRENT, phải giữ dữ liệu/công việc khi mở rộng.
- Một doanh nghiệp/Gmail/staff, một image React/FastAPI/Cloud Run với Cloud SQL/private GCS/Secrets/Scheduler. Không multi-tenant/omnichannel/payment hoặc sao chép Chatwoot.
- WORKFLOW định nghĩa states; DATABASE schema; API wire; SHARED interfaces/owner; TASK việc hiện hành. Mâu thuẫn nêu rõ bằng chứng và báo owner trước thay contract.
- CURRENT13 bảng/203 cột/migration0005 không đủ KB/settings/per-role history. CR-001 trong DATABASE đề xuất7 bảng mới, PROPOSED/PENDING_REVIEW. Không coi docs rewrite là duyệt migration. Review A+B+C và authorization triển khai riêng trước đổi schema/wire.
- Không sửa schema_v1.py/backfill_v1.py hoặc migration đã áp dụng; không nhét thực thể/keys mới vào JSON legacy. Một migration chain do A tổng hợp sau review.

## Phân công và tích hợp
- A fullstack workspace/auth/intake/search/settings/orchestration/platform; B fullstack lookup/policy/KB/retrieval/evidence; C fullstack decision/composer/safety/citations/send/lifecycle.
- Giữ FS-A1..A4/B1..B4/C1..C4. BASE chuẩn bị contracts/harness; ALL1 nghiệm thu chung, không task thuyết trình.
- Mỗi người một worktree/nhánh từ baseline chung, không tự spawn agent. Không tự commit/push/merge/reset/clean hoặc xóa dữ liệu khi chưa có yêu cầu.
- A sở hữu shared composition/main/App/config/models/API helper/locks; B/C sửa domain, gửi interface/env/deps manifests cho A. Dùng existing mappings; không định nghĩa trùng Table/Base.
- Cross-domain mutation qua CaseStore UoW/version/audit, join cùng transaction. Không nested commit hoặc network trong row lock. B/C có harness/doubles test/dev để bắt đầu; production cấm fake success/auth bypass.
- Điều phối AI roles không đồng nghĩa coding agent được spawn subagents hoặc thực hiện staff actions.

## Safety và nghiệm thu
- Nhân viên quyết định rồi preview đúng final revision và confirmed send. Agent/approve/Scheduler không gửi; không payment/fulfillment/close tự động. Live send cần task rõ và mailbox nhóm kiểm soát.
- Email/ảnh/KB nháp không đáng tin; không URL fetch/tool execution hoặc secret/PII vào prompt/log/Git/frontend. Only eligible approved KB làm nguồn; giữ source/settings/context snapshot.
-96 test đặc tả (78 cũ+18 mới) không phải92 tests automated lịch sử; trạng thái NOT_RUN/FAIL/BLOCKED không là PASS. Chưa cloud thật không ALL1 PASS.
- Bàn giao task/owner/commit/files/contract-env-deps delta/test IDs+biến thể/mock-DB-browser-live-cloud/evidence/blocker/reviewer. Owner đề nghị REVIEW, người khác xác nhận VERIFIED. SC pilot chưa đo phải NOT_RUN.
