# C — fullstack Resolution và Communication

## Prompt copy cho AI

> Đọc AGENTS → CONTEXT → WORKFLOW → SHARED_CONTRACTS → TASK → task này; đọc API/DATABASE/UI_UX/ERROR_HANDLING/SECURITY/TESTING và C_TEST_CASES. Bạn làm FS-C1..FS-C4: dùng decision/reply/operation models sẵn có, tự làm schemas/router/services, DecisionPanel/ReplyComposer/FulfillmentPanel/history và tests. Bạn không là người lo toàn Google/cloud. Dùng BASE CaseContext/CaseStore/Principal/GoogleClientFactory doubles để code fullstack trước, không chờ A backend hay B policy/AI. Tự implement reserve/complete/idempotency/reconcile, không đợi A viết. AI/manual prepare, preview/save/send theo nhân viên xác nhận, Gmail draft phụ, workflow fulfillment/close/reopen. Scope Google compose và send probe thuộc phần bạn, A quản nền Cloud Run. Không tự gửi theo AI/Scheduler, không payment. Bàn giao tests/evidence MERGE/RELEASE và manifests shared, production không fake.

## Việc được giao

BASE ngày14/11 đã có ComplaintDecision/CaseReply/ReplyOperation và cột lifecycle trong app/models.py/schema0005; dùng mappings đó (có thể re-export vào domain), không tạo lại bảng/model/migration. Reserve/complete/CaseStore/Principal/harness và toàn bộ UI/API nghiệp vụ vẫn cần triển khai. Không suy từ schema rằng đã có Gmail send; xem IMPLEMENTATION_REPORT.

- **FS-C1:** decision/resolution/missing_fields/note/assessment snapshot, nhiều vòng/optimistic version/history API và UI. Không khóa request info thành ngõ cụt hoặc auto-close sau approve.
- **FS-C2:** prepare AI/manual, body save/revision, preview, stale/review-context và composer UI/API. Own text provider cho phản hồi dùng config chung; không chờ B extraction chạy được để soạn từ CaseContext factory.
- **FS-C3:** Gmail write module riêng, Unicode MIME/thread/recipient, direct send hoặc saved draft update/send, external edit hash, operation reserve/complete/unknown/reconcile; API + composer busy/error states. Bạn sở hữu các transaction nghiệp vụ này qua shared UoW A, không phụ thuộc service quyết định/gửi do A viết.
- **FS-C4:** ghi nhận thực hiện ngoài app, resolved/close/reopen/note/audit + FulfillmentPanel/HistoryPanel và full-loop domain tests. Không tích hợp payment/kho hoặc làm slide/demo.

## File, schema và independent harness

Theo CLAIMPILOT_MVP_DB_V1, C dùng ComplaintDecision/CaseReply/ReplyOperation đã có từ BASE; composite FK cùng case/reply đã được tạo, không khai báo lại metadata. Reserve lưu immutable request_snapshot, confirmed_at/by, idempotency và unsettled partial unique; completion cần outbound+sent_message_id+sent_at cùng transaction. Fulfillment/closure metadata đã có cột trên complaints, không thêm bảng hoặc field JSON tùy ý lúc code. Không migration/ALTER riêng sau BASE; key/model mới chỉ config.

Resolution module backend + frontend thuộc C; decisions/replies/operations mappings đã có, C viết logic và DTO theo DB chốt. Field lifecycle core được khai báo trong BASE; A aggregate migration/settings/lock theo manifest C. Không sửa main/App/models/config trực tiếp cùng A/B.

Dùng own decision/reply/operation factories, CaseContext verified/unknown versions, fake CaseStore/Google client và Principal trong isolated test app; không cần A sync hoặc B UI để viết/test fullstack. Khi ghép nối primitive append outbound/UoW thật; B snapshot thật chỉ cần đúng contract, C không import ORM B.

Network nằm ngoài transaction: reserve → Gmail → completion UoW mới, idempotency persistent. Inbound đến sau reserve vẫn lưu qua A, completion không đè needs_review. Tắt auto retry Gmail write SDK; unknown không tự resend/reset. Case sent không sửa body hoặc gửi lại.

## DoD

[Tests C](../test-cases/C_TEST_CASES.md) đủ MERGE/RELEASE; controlled Gmail send sau click và draft thật; request-info nhiều vòng; lifecycle đóng/mở đúng. Bàn giao UI/models/API/env/deps/tests/evidence+reviewer. A làm cloud platform, bạn xác minh chức năng riêng trên revision chung, không giao phần gửi/timeline cho A/B viết hộ.
