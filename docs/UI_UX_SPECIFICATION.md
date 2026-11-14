# UI/UX — Workspace AI-first v4

Nguồn REQ-001–032 tại [yêu cầu](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md); wire tại API_SPECIFICATION. Chatwoot chỉ tham khảo cách tổ chức, không sao chép tài sản/giao diện.

## Điều hướng
Sidebar desktop có nhận diện một doanh nghiệp và5 mục: Tổng quan, Hộp thư, Knowledge Base, Dữ liệu & Tích hợp, Cài đặt. Không giả nút chuyển tenant. Dùng query tab=overview|inbox|knowledge|data|settings; detail giữ ?tab=inbox&case=ID và bộ lọc queue/workflow_status/processing_status/complaint_type/q/page. URL không chứa body/email/token; q từ khóa được giữ trong state phiên UI, không ghi vào URL/log.

Tổng quan: workflow counts, xử lý AI tách riêng, agent active/failed/waiting, last sync/deferred và ngoại lệ. Hiển thị unavailable thay số0 khi API lỗi.

## Hộp thư
Desktop ba vùng: list có search/filter → ConversationPanel → context với Assessment/Evidence/AgentProgress/Sources; Decision/Composer/Fulfillment trong vùng detail cuộn được. Không modal hẹp. Trở lại giữ filter/page; deep-link phục hồi sau login.

Mobile390px: list→detail một cột, tabs Hội thoại/Đánh giá/Lịch sử. Form/note/body state ở feature parent nên đổi tab không mất; có unsaved edits khi đổi case thì hỏi bỏ/lưu, không tự gửi. Nút không che textarea, keyboard/focus/aria-live và nhãn đầy đủ; thời gian Asia/Ho_Chi_Minh.

## AgentProgress và Sources
6 vai trò: intake_classification, order_lookup, policy_assessment, evidence_analysis, reply_writer, safety_quality. Mỗi bước hiển thị queued/running/completed/failed/waiting_data/stale/skipped, attempt/time/source/error. skipped có lý do và không giả completed. Lượt cũ có mục history; trạng thái agent không đổi thành rejected/resolved.
Nguồn mở bằng ID/version trong app, gồm order/policy/KB/asset; snippet là text escaped. Không có nguồn, bất đồng hoặc stale có banner review_required và đường manual/retry. Confidence thiếu để null; không dựng phần trăm chắc chắn.

## Knowledge Base
List q/topic/status; editor title/body/topic/source_label/source_reference/valid_until/review_due_at. Các trạng thái draft/pending_review/approved/archived; nút gửi duyệt và duyệt/publish riêng, dù MVP dùng cùng một account. Khi sửa published article tạo revision draft mới; agent chỉ đọc revision đã duyệt, còn hiệu lực, không conflict. Trang history mở citation đúng revision cũ với badge nếu bị superseded/archive/expiry; không tự chuyển link cũ sang nội dung mới. Conflict flag có note; editor dirty/validation/409/loading/publish failed giữ input.

## Dữ liệu & Tích hợp và Cài đặt
Data: Gmail presence khác connectivity, last_attempt/success/error/deferred/intake failures; xem orders/policy versions/nguồn KB, unknown giữ null, không public API seed/reset.
Settings: display_name/language/tone, optional evidence role, confidence-review threshold và cấu hình escalation. Lưu phải có server confirmation/revision; invalid422, stale409 giữ form; failure không hiện Saved. Không có nút tắt auth, safety, staff decision/confirm send. Thay settings áp dụng lần tạo nội dung mới, không sửa retroactive reply cũ.

## Decision/Composer và lifecycle
Giữ semantics WORKFLOW: staff chọn approve/reject/request_information, không Approve-and-send. AI/manual draft → lưu nội dung → xem nguồn và quality findings → preview To/subject/body → confirmed send. Draft Gmail là nút phụ, không coi draft là sent. Edit/new inbound/source/config thay đổi làm check/preview trước mất hiệu lực theo API.
Unknown hiển thị chưa rõ kết quả, chặn gửi lại mù; sent chỉ nghĩa Gmail đã nhận gửi. Thiếu căn cứ không tự approve/refund/close; cho sửa/manual nhưng vẫn qua safety và xác nhận. Fulfillment ghi thực hiện ngoài app + reference/note; close/reopen theo WORKFLOW. AI/panel lỗi vẫn đọc được history.

## Owner và nghiệm thu
A shell/login/nav/queues/settings/data/progress container; B KB editor/Assessment/Evidence/source browser; C Decision/Composer/Quality/Fulfillment. Panel props caseId/onCaseChanged; nguồn data/settings revision qua shared contracts.
AC01–18; desktop/mobile keyboard, dirty form qua tab/401, unavailable numbers, nguồn nháp không làm căn cứ, safety/error/stale hiển thị đúng.
