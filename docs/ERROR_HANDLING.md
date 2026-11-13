# Error handling — TARGET v2

Owner v3 theo feature: A intake/auth/sync/cloud, B policy/manual/evidence/text, C decisions/replies/Gmail write/lifecycle; shared errors/wire codes không đổi vì chia người. UI/API/tests lỗi của phần nào do fullstack phần đó làm, không chờ một người viết frontend hoặc backend chung.

API giữ detail string và thêm code stable; Pydantic validation 422 có thể array. Error không đồng nghĩa quyết định bị mất. Raw provider exception/stacktrace không tới UI.

| HTTP/code | Hành vi | Retry |
|---|---|---|
| 401 invalid_credentials/session_expired | lỗi chung hoặc login; giữ route, không replay POST | login lại |
| 403 csrf_invalid/forbidden_scheduler | không thực hiện mutation | sửa phiên/quyền |
| 404 complaint_not_found/reply_not_found | không tồn tại, không fake success | refresh khi phù hợp |
| 409 stale_version/stale_reply | giữ note/body, lấy detail mới | người dùng review context |
| 409 reply_busy/sync_busy/evidence_busy | operation đang chạy | refresh/poll, không gửi lặp |
| 409 invalid_case_state/ownership_unverified | nêu bước cần hoàn tất | xác minh hoặc sửa flow |
| 409 idempotency_conflict | key đã dùng payload/operation khác | client sửa key chỉ cho intent mới, không resend unknown |
| 409 external_draft_changed | preview local/remote | người dùng chọn giữ local có audit hoặc dừng |
| 409 reply_unknown | chưa rõ draft/send kết quả | đối soát, không resend mù |
| 422 evidence_missing/invalid_image | thiếu/không hợp lệ; một phía vẫn được phân tích | bổ sung ảnh |
| 503 database_unavailable | transaction rollback, không success | DB phục hồi |
| 503 provider timeout/quota | raw email giữ lại; failed badge riêng | manual hoặc retry bounded |
| 503 gmail authorization/permission | decision/body giữ nguyên | consent lại, không lặp call |
| 503 gmail_explicit_rejection | reply failed, operation failed | sau sửa nguyên nhân, click xác nhận mới |

## Ma trận kết quả Gmail

- Chưa thực hiện request hoặc provider từ chối chắc chắn (ví dụ quyền không đủ): failed; không nói đã gửi.
- Có response success và persist DB thành công: sent/draft_saved; ghi ID, outbound message, audit. Sent không phải delivered/read.
- Timeout/disconnect sau dispatch, HTTP 5xx có thể đã có side effect, process chết hoặc persist thất bại sau success: unknown. Nếu DB đang down, row còn sending/draft_saving; lần đọc/recovery sau 5 phút chuyển unknown.
- Không auto retry mutations Gmail trong SDK. Idempotency key chỉ bảo vệ request qua app, không là bảo đảm idempotency của Gmail.
- `scripts.reconcile_replies` (C triển khai) nhận reply UUID: dùng draft ID/sent ID nếu có, Message-ID ổn định, thread, người nhận và khoảng thời gian để tìm ứng viên. Một match chắc chắn → persist kết quả/audit; nhiều match hoặc không đủ căn cứ → giữ unknown. Không tìm thấy không chứng minh chưa gửi; không reset tự động.
- Reset unknown về failed để thử lại chỉ do người vận hành xác nhận sau kiểm tra mailbox, ghi audit lý do; script không gửi email. Không thêm nút reset công khai MVP.

Theo schema CLAIMPILOT_MVP_DB_V1, khi reset/reconcile phải cập nhật cả reply và reply_operations unsettled trong cùng UoW. Partial unique chặn cả in_progress và unknown; không chỉ đổi reply.status để lách khóa hoặc để operation unknown mồ côi. Parse/fetch lỗi trước case lưu gmail_intake_failures; sau recover message đã lưu thì resolve failure, lỗi AI tiếp theo lưu text_analysis_runs riêng.

## Snapshot và concurrency

AI finish sau manual edit giữ kết quả gốc ở message nhưng không overwrite current projection. Evidence finish làm context stale; reply chưa gửi cần review. Gửi hoàn tất khi inbound mới vừa đến vẫn persist sent message nhưng giữ needs_review. Sửa quyết định không xóa history/outbound cũ.

## Logging

Event/request/case/reply/operation ID, code và duration; không cookie/password/token, raw email/ảnh hoặc prompt. integration_state lưu last_attempt/last_success/error/deferred. UI nói hành động cần làm, không lộ thông số nội bộ. Không đổ mọi lỗi kỹ thuật thành “không đủ điều kiện”.
