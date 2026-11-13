# Acceptance matrix — tiêu chí bàn giao v2

Mọi dòng khởi tạo NOT_RUN: đây là đặc tả, không bằng chứng đã đạt. “Có code” không thay Google/cloud thật. FR tham chiếu SRS. Ghi kết quả triển khai trong TASK, không sửa tiêu chí để hợp thức hóa lỗi.

Chi tiết kiểm thử theo task: [A fullstack](test-cases/A_TEST_CASES.md), [B fullstack](test-cases/B_TEST_CASES.md), [C fullstack](test-cases/C_TEST_CASES.md). Đây là các kiểm tra phần việc; bảng AC dưới đây kiểm tra liên thông toàn sản phẩm. Pass test phần riêng không tự làm AC tương ứng PASS; dùng [completion gate và mẫu evidence](TESTING_GUIDELINES.md).

| ID | FR | Kịch bản và kết quả bắt buộc | Bằng chứng / owner | Trạng thái |
|---|---|---|---|---|
| AC01 | FR03/05/11 | Giao trễ → approve shipping fee refund → edit/preview/send → waiting_fulfillment → ghi thực hiện ngoài app → resolved → close; không tự refund | DB/browser + email thật tới nhóm / C+A | NOT_RUN |
| AC02 | FR02/03/06 | Damaged → request ảnh → send → waiting_customer → reply chỉ “Tôi gửi ảnh” cùng thread → append ảnh/needs_review → Gemini → decision mới → reply mới | DB/browser + Gmail intake/ảnh thật / A+B+C | NOT_RUN |
| AC03 | FR04/10 | Sender mismatch chặn approve và không lộ order trong thư yêu cầu → manual verification có căn cứ → approve; đổi order reset verification | DB/browser / B+C | NOT_RUN |
| AC04 | FR04/10 | AI timeout hoặc sai order/type → giữ original → manual correction/reassess → manual reply và xử lý tiếp | mocked provider + DB/browser / B+C | NOT_RUN |
| AC05 | FR05 | Prepare không tạo Gmail draft; save draft thật → sửa local → sync/send nội dung cuối sau confirm; remote edit conflict có review | mocked MIME tests + Gmail draft/send controlled / C | NOT_RUN |
| AC06 | FR03/05 | Inbound/decision/revision mới trước send → 409 stale; context review hoặc reply mới; concurrent inbound sau reserve không bị completion đè | concurrent DB + browser / A+B+C | NOT_RUN |
| AC07 | FR02/11 | Closed nhận inbound mới tự mở lại; cùng Gmail ID không nhân đôi; outbound không reopen; new thread cùng order chỉ suggested relation | DB + controlled Gmail / A+C | NOT_RUN |
| AC08 | FR05 | Double click/idempotency, timeout sau dispatch, process chết, persist error sau send → không auto resend, unknown/reconcile/audit | mocked fault tests + DB / C+A | NOT_RUN |
| AC09 | FR06 | Hai phía comparison; một phía single_side/inconclusive; không ảnh 422; MIME sai/quá byte/pixel bị chặn; anonymous content bị từ chối | unit/DB/browser + Gemini comparison thật / B | NOT_RUN |
| AC10 | FR01 | Login/logout/expired, Origin/CSRF, business anonymous 401, internal invalid OIDC bị chặn, không token frontend | API/browser / A+B+C | NOT_RUN |
| AC11 | FR04/09 | Đủ năm nhóm, vấn đề khác yêu cầu, thiếu/unknown/order-date-boundary, seed hai lần và giữ ngày khiếu nại đầu khi bổ sung | unit/DB + seed / B+A | NOT_RUN |
| AC12 | FR07/08/09 | URL HTTPS, migration/backfill một head, Scheduler run-now + lịch thật, thread cursor/deferred, last sync rõ, new revision giữ DB/token/ảnh | cloud logs/revision + controlled live smoke / A+B+C | NOT_RUN |

## Format ghi bằng chứng

`AC-ID | task | time Asia/Ho_Chi_Minh | commit/revision | command/action | mock/DB/browser/live/cloud | result | limitation/blocker`.

Không gửi mail khách thật, không thực hiện giao dịch thật, không lưu secrets/body thật trong tài liệu. Khi live integration blocked, ghi BLOCKED đúng hạng mục; không thay fixture rồi đánh dấu PASS live.

Phân công AC theo feature v3, mã test FS và owner trong ba bộ test fullstack; từng case có mã cũ để đối chiếu; 78 cases vẫn giữ NOT_RUN. Bản nghiệm thu phải là Cloud Run thật, không task diễn tập. BASE/harness là thiết kế chuẩn bị, không bằng chứng runtime đã có.
