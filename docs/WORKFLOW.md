# Luồng chuẩn và state machine — TARGET v2

Đây là nguồn chuẩn enum nghiệp vụ. Một hồ sơ có nhiều messages, decisions, replies và audit events. Tên `complaints`/ID cũ được giữ để tương thích; UI gọi là hồ sơ. Một Gmail thread ↔ tối đa một hồ sơ trong mailbox demo. Một hồ sơ chọn một đơn; nhiều đơn/khác chủ đề được gắn needs_manual_review, không tự tách/gộp.

## Các trạng thái độc lập

| Chiều | Enum | Ý nghĩa |
|---|---|---|
| workflow_status | needs_review, waiting_customer, waiting_fulfillment, resolved, closed | Công việc doanh nghiệp |
| processing_status | pending, processing, completed, failed | Phân tích dữ liệu, không phải hoàn tất khiếu nại |
| ownership_status | unverified, email_matched, manually_verified, mismatch | Xác minh chủ đơn; email_matched chỉ là tín hiệu |
| decision action | approve, reject, request_information | Mỗi lần quyết định là event mới |
| resolution | shipping_fee_refund, order_refund, replacement, reshipment, carrier_investigation, decline, request_information, other | Phương án doanh nghiệp chọn |
| fulfillment_status | not_required, pending, completed | Thực hiện bên ngoài app, không phải payment API |
| reply status | prepared, draft_saving, draft_saved, sending, sent, failed, unknown | Trạng thái side effect Gmail |
| reply operation status | in_progress, succeeded, failed, unknown | Mỗi intent save_draft/send có idempotency key |
| evidence status | pending, completed, failed | Job phân tích ảnh |
| consistency | consistent, inconsistent, inconclusive | Nhận xét hỗ trợ, không phải kết luận gian lận |

decision_status là projection hiện hành: undecided/approved/rejected/more_information_requested. Processing error không đưa hồ sơ ra khỏi hàng đợi nghiệp vụ. is_complaint NULL được thấy ở hàng đợi kỹ thuật; false được ẩn khỏi danh sách khiếu nại nhưng không bị xóa.

## Luồng

```mermaid
flowchart TD
  A[Email mới hoặc bổ sung] --> B[Tạo/cập nhật hồ sơ và tăng version]
  B --> C[AI hỗ trợ hoặc xử lý thủ công]
  C --> D[Xác minh, policy và ảnh]
  D --> E[Nhân viên quyết định phương án]
  E --> F[Xem/sửa phản hồi]
  F --> G[Lưu nháp hoặc xác nhận gửi]
  G --> H{Đã gửi thành công?}
  H -->|Yêu cầu thông tin| I[Chờ khách]
  I --> A
  H -->|Chấp thuận| J[Chờ thực hiện bên ngoài]
  J --> K[Nhân viên ghi nhận đã thực hiện]
  H -->|Từ chối| L[Đã giải quyết]
  K --> L
  L --> M[Nhân viên đóng hồ sơ]
  M -->|Khách trả lời mới| A
```

## Chuyển trạng thái

| Sự kiện | Điều kiện | Kết quả |
|---|---|---|
| Email inbound mới | Gmail ID chưa có | Lưu message một lần; needs_review; version+1; outbound không mở lại hồ sơ |
| Đánh giá/đính chính/xác minh/ảnh mới | Đủ input, không đang dispatch gửi | Lưu snapshot/audit; version+1; needs_review; phản hồi chưa gửi cần xem lại |
| Quyết định | version khớp; có hồ sơ complaint hoặc đã xác nhận thủ công | Append decision, current_decision_id mới; needs_review; version+1 |
| Lưu draft | Nội dung hiện hành | draft_saved; workflow không đổi, chưa chờ khách |
| Gửi request_information | Decision/reply/version hiện hành, Gmail xác nhận | waiting_customer; fulfillment not_required |
| Gửi reject | Như trên | resolved; fulfillment not_required |
| Gửi approve | Chủ đơn được xác minh; phương án cụ thể | waiting_fulfillment; fulfillment pending |
| Ghi nhận thực hiện | Latest approve đã gửi; không có inbound/context mới | fulfillment completed; resolved; audit bằng chứng thủ công |
| Đóng | resolved, latest decision đã có reply sent trả lời latest inbound; không unknown/busy hoặc inbound mới chưa xem | closed, ghi chú/audit |
| Mở lại thủ công | closed/resolved + lý do | needs_review, tăng version, lưu audit |

Approve dùng resolution thuộc shipping_fee_refund/order_refund/replacement/reshipment/carrier_investigation/other. Reject dùng decline; request_information dùng request_information và missing_fields không rỗng. Ghi chú 1..2000 bắt buộc. Approve khi ownership unverified/mismatch bị chặn; có thể xác minh thủ công có căn cứ. Policy not_eligible không khóa quyết định ngoại lệ, nhưng phải ghi lý do.

Quyết định không sửa/xóa: thêm quyết định mới và đánh dấu reply cũ stale. Nếu approve cũ đã gửi, đổi phương án cần ghi rõ quyết định mới thay thế và fulfillment trước đó trong audit; không tự đảo giao dịch. Cho phép nhiều vòng request_information → inbound → review → decision. Không tái dùng reply đã gửi cho quyết định mới.

## Version và nội dung cũ

- `case_version` tăng khi inbound mới, decision, sửa/xác minh/reassessment, evidence hoàn tất, fulfillment hoặc close/reopen. Không tăng chỉ vì người dùng mở màn hình hoặc lưu reply.
- Reply lưu `basis_case_version`, `decision_id`, `in_reply_to_message_id`, `revision`. Sửa body tăng revision. Gửi/lưu Gmail draft yêu cầu expected_case_version và expected_reply_revision khớp, cùng current decision và latest inbound.
- case_version thay đổi: reply chưa gửi trở thành is_stale=true (tính từ basis). API review-context cho nhân viên xem thay đổi, xác nhận dùng nội dung đã kiểm tra rồi cập nhật basis; không tự bỏ cảnh báo.
- Quyết định khác thì phải prepare reply mới. Review-context không được đổi decision_id của reply cũ.
- Đính chính thay đổi order/type/requested_action/ownership làm mất hiệu lực quyết định hiện hành: current_decision_id=null, needs_review; cần quyết định/reply mới, không dùng review-context để hợp thức hóa quyết định cho đơn khác. Lịch sử và hành động đã gửi/thực hiện không bị xóa.
- Reply sent là lịch sử và không có stale flag; case_version tăng vì fulfillment/close không buộc gửi lại thư. Context nghiệp vụ mới sau sent đưa hồ sơ needs_review; để giải quyết tiếp cần decision/reply mới. API review-context không sửa thư đã gửi.
- Closed không cho review/decision/reply mới cho tới reopen (thủ công hoặc inbound). Reopen không tự gửi gì. Manual review xác nhận complaint cho candidate lỗi cho phép processing_status completed với nguồn manual, không báo AI đã thành công; raw message vẫn giữ processing_error gốc.
- Không có network trong row-lock transaction. Serialize thay đổi case với bước reserve gửi; context đến sau reserve vẫn được lưu nhưng gắn cảnh báo concurrent_inbound. Không hứa hủy được email đã được Gmail nhận.

## Giới hạn có chủ đích

Một Gmail, một account staff, một đơn/hồ sơ, chỉ ảnh JPEG/PNG. Không multi-tenant, thanh toán, kho, video, SLA phức tạp hoặc công cụ split/merge. Mọi trường hợp vượt giới hạn có hàng đợi thủ công, không bị tự từ chối hoặc âm thầm bỏ qua.
