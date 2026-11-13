# UI/UX specification — hồ sơ nghiệp vụ TARGET v3

Cho phép đổi bố cục chi tiết để đáp ứng vòng xử lý, giữ stack/component/CSS hữu ích. Không để giới hạn modal cũ quyết định sản phẩm. Không lộ tên bảng/config/stacktrace trong flow nhân viên.

## Màn hình và wireframe desktop

```text
┌ ClaimPilot     Gmail: kết nối | Sync thành công lúc ... | Đồng bộ | Staff/Đăng xuất ┐
│ Cần xử lý | Chờ khách | Chờ thực hiện | Đã giải quyết | Đã đóng | Lỗi cần kiểm tra  │
├ Danh sách hồ sơ ──────┬ Cuộc trao đổi ────────────────────┬ Thông tin xử lý ────────┤
│ mã đơn / chủ đề      │ inbound + outbound theo thời gian │ đơn / xác minh / sửa   │
│ mức ưu tiên          │ ảnh đính kèm đúng email           │ policy + thiếu gì      │
│ trạng thái / cập nhật│ timeline quyết định/audit         │ ảnh đơn ↔ ảnh khách    │
├──────────────────────┴───────────────────────────────────┴─────────────────────────┤
│ Bước tiếp theo | Phương án + ghi chú | Xem/sửa phản hồi | Lưu nháp / Gửi phản hồi  │
└───────────────────────────────────────────────────────────────────────────────────┘
```
Desktop chi tiết có thể là trang riêng hoặc panel trong dashboard nhưng phải có deep-link `?case=ID`, giữ filter khi quay lại. Chốt MVP: dùng trang/panel chiếm toàn vùng nội dung với nút Quay lại, không modal hẹp chứa toàn workflow. Mobile 390px: list → detail một cột; tabs Trao đổi/Đánh giá/Lịch sử, action ở cuối, không overlay che textarea.

## Component và nguồn dữ liệu

| Component | Nội dung/API |
|---|---|
| LoginPage/SessionHeader | auth/me/login/logout; không localStorage session |
| CaseQueue/CaseList | workflow_counts, priority, order, last_message_at; queue technical cho candidate AI lỗi |
| ConversationPanel | messages inbound/outbound, subject/body text, attachments; không render HTML email |
| AssessmentPanel | verified order, ownership, policy reason/version/missing_fields/next_action; sửa dữ liệu thủ công |
| EvidencePanel | ảnh nguồn rõ, mode một/hai phía, observations/limitations/missing_evidence |
| DecisionPanel | action + resolution + note; lịch sử không khóa vĩnh viễn |
| ReplyComposer | latest reply/decision/version, recipient/subject readonly, body editable, save draft/send |
| FulfillmentPanel | chờ thực hiện, ghi nhận ngoài app + reference, resolved, close/reopen |
| Timeline | messages + decisions + audit, actor/time, sửa gì và lý do |

## Điều kiện nút và hành vi

| Action | Được dùng khi | Loading/lỗi |
|---|---|---|
| Sửa mã đơn/phân loại | hồ sơ chưa closed, không operation gửi đang chạy | form có note; 409 giữ input và lấy context mới |
| Xác minh thủ công | có order, có căn cứ và note | reset khi đổi đơn; chưa xác minh vẫn gửi yêu cầu thông tin an toàn được |
| Approve | complaint xác nhận, có order/ownership, resolution/note đủ | policy khác không tự chặn; cảnh báo ngoại lệ |
| Reject/Request information | complaint xác nhận, note đủ; request cần checklist thiếu gì | không đòi AI completed nếu đã review thủ công |
| Soạn bằng AI / Viết thủ công | có current decision | AI lỗi giữ dữ liệu, cho chọn thủ công |
| Lưu nháp | nội dung đã lưu, không stale/unknown/busy/sent | draft_saved chưa đổi sang chờ khách |
| Gửi phản hồi | các điều kiện server trong API, user đã xem preview | xác nhận To + subject + body cuối; disable double click |
| Ghi đã thực hiện | latest approve đã gửi, context hiện hành | nêu đây là thao tác ngoài app, không nút thực hiện refund |
| Đóng | resolved + latest reply sent, không outstanding conflict/unknown | note bắt buộc, đóng không xóa hồ sơ |
| Mở lại | resolved/closed | lý do, quay về needs_review |

## Composer và chống gửi nhầm

1. Chọn phương án ở DecisionPanel, không dùng một nút Approve-and-send.
2. Prepare reply; hiển thị đúng recipient, chủ đề và decision nguồn. Preview không phải tạo nháp Gmail.
3. Edit body → Lưu nội dung (PATCH) → preview. Không cho send khi còn unsaved edits.
4. Nút chính Gửi phản hồi, nút phụ Lưu nháp vào Gmail. Send xác nhận nội dung cuối một lần; không thêm xác nhận lặp.
5. Inbound/decision/context mới: banner “Hồ sơ đã thay đổi”, giữ body; cập nhật context và đọc lại trước review-context. Decision mới yêu cầu reply mới.
6. draft_saved vẫn sửa body local; UI nhắc thay đổi chưa đồng bộ Gmail. Remote edit conflict hiển thị nội dung local/remote; MVP chỉ chọn giữ local có xác nhận hoặc hủy để kiểm tra Gmail, không tự merge.
7. unknown: “Chưa xác định Gmail đã gửi/lưu hay chưa”; không bật retry mù. sent chỉ nói “Đã gửi qua Gmail”, không nói khách đã nhận/đọc.

## State inventory

- Trang: loading/empty list/no filter match/network error/session expired.
- Hồ sơ: needs_review/waiting_customer/waiting_fulfillment/resolved/closed; processing badge riêng, không trộn màu AI lỗi và reject.
- Reply: prepared/draft_saving/draft_saved/sending/sent/failed/unknown + unsaved/stale flags; busy poll có giới hạn.
- Evidence: no images/one side/ready/pending/completed/failed; thiếu ảnh gốc không khóa xử lý.
- 401 về login, giữ đường dẫn nhưng không tự replay POST; 403 nêu không thực hiện; 409 giữ draft/note và refresh; 503 giữ nội dung.

## Accessibility và nghiệm thu

Label/validation từng field, keyboard tới mọi action, focus sau navigate/confirm quay lại nút nguồn, aria-live cho kết quả. Không dùng màu làm dấu hiệu duy nhất. Ảnh có alt và phóng to trong viewport, không tràn 390px. Hiển thị giờ Việt Nam, policy demo, active text provider/model thật. Test theo [acceptance](ACCEPTANCE_MATRIX.md), không chỉ screenshot đẹp.

## Quyền sở hữu fullstack

A làm WorkspaceShell/Login/queues/conversation/SyncStatus và API/dữ liệu tương ứng; B tự Assessment/ManualReview/Evidence cùng router/models/providers; C tự Decision/ReplyComposer/Fulfillment/History cùng router/models/Gmail write. Không còn B viết toàn frontend. BASE chốt feature slots/props `{caseId,onCaseChanged}`; A compose ba panel, domain UI tự fetch API own, cùng shared api client/session contract. Mỗi panel loading/error độc lập, event invalidate không tự gửi lại mutation. Không task làm slide/diễn tập trong UI backlog.

Schema CLAIMPILOT_MVP_DB_V1 đã có fulfillment/closure actor/time/reference/note, proposed_amount/currency, lịch sử text runs và intake failures. UI đọc API projection, không yêu cầu agent tự thêm cột cho timeline hoặc trạng thái. Lỗi fetch/parse chưa có case hiển thị metadata sanitized từ integrations/intake-failures trong vùng lỗi, không mở detail complaint giả; AI run history là lưu trữ nội bộ, không bắt thêm màn hình debug AI.

Số tiền đề xuất chỉ hiển thị khi có căn cứ từ order và decision.proposed_amount; currency VND. Total amount chưa biết thì không tự điền0/ước đoán hoặc hứa đã hoàn tiền. Dữ liệu thực hiện/đóng lấy timestamp/actor/reference/note theo API, timeline giữ các lần trước qua audit.

Ảnh đơn dùng evidence_kind packing/delivery để gắn nhãn “Ảnh đóng gói” hoặc “Ảnh giao hàng”; ảnh khách kind customer. Không suy ra giai đoạn chỉ từ thời điểm upload và không dùng ảnh đóng gói để khẳng định đã giao thành công.
