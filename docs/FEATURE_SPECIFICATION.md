# Feature specification — sáu hạng mục, TARGET v3

Luồng/enum tại [WORKFLOW](WORKFLOW.md), wire tại [API](API_SPECIFICATION.md), persistence tại [DATABASE](DATABASE_DESIGN.md). Mỗi hạng mục đủ 11 thành phần; acceptance IDs tại [matrix](ACCEPTANCE_MATRIX.md).

## F1 — hồ sơ, quyết định, manual review và hoàn tất (FR02/03/10/11)

1. **Objective:** xử lý trọn hồ sơ qua nhiều vòng và truy vết.
2. **User Story:** nhân viên xem toàn bộ cuộc trao đổi, xác minh/sửa dữ liệu, chọn phương án và theo dõi đến đóng.
3. **Acceptance Criteria:** nhiều email/decision; request info không khóa; approve/reject không tự đóng; manual review có lý do; latest context/version được kiểm tra.
4. **UI/UX:** Conversation/Assessment/Decision/Fulfillment/Timeline, bước tiếp theo rõ; không nhầm eligible với approved.
5. **API Contract:** messages/review/reassess/decisions/fulfillment/close/reopen trong API.
6. **Error Handling:** 409 refresh giữ input, DB rollback không success; AI lỗi vẫn review thủ công.
7. **Edge Cases:** hai tab, inbound lúc quyết định, sai chủ đơn, nhiều đơn/thread, khách trả lời sau closed, đổi phương án sau gửi.
8. **UI States:** workflow badge và processing badge độc lập; manual/conflict/submitting/saved; không khóa decision suốt đời.
9. **Test Cases:** AC01/02/03/04/06/07, atomic/audit/version và source manual.
10. **DoD:** DB + browser flows đạt, audit sau reload, nhiều vòng có thể kết thúc.
11. **Out of Scope:** payment/warehouse API, multi-user roles, split/merge UI, xóa lịch sử.

## F2 — phản hồi, gửi có xác nhận và nháp (FR05)

1. **Objective:** phản hồi trong app sau khi nhân viên kiểm tra, có lưu nháp khi cần.
2. **User Story:** chọn quyết định, soạn AI/manual, sửa nội dung, gửi hoặc lưu nháp.
3. **Acceptance Criteria:** nội dung đã lưu đúng revision; recipient/thread đúng; user xác nhận send; duplicate/unknown không gửi mù; sent gắn Gmail ID.
4. **UI/UX:** preview không phải draft Gmail; edit/save/confirm send, Lưu nháp phụ; stale/unknown/external edit rõ.
5. **API Contract:** replies prepare/PATCH/review-context/draft/send/GET; idempotency_key theo API.
6. **Error Handling:** AI lỗi cho manual; explicit Gmail reject có retry; ambiguous timeout unknown cần reconcile; không mất decision/body.
7. **Edge Cases:** token readonly, remote draft bị sửa/xóa/gửi ngoài app, DB lỗi sau Gmail success, inbound đang gửi, send repeated.
8. **UI States:** prepared/draft_saving/draft_saved/sending/sent/failed/unknown, unsaved và stale riêng.
9. **Test Cases:** AC01/05/06/08; MIME Unicode, đúng To/thread, không tự generate khi send.
10. **DoD:** email thật tới mailbox nhóm kiểm soát sau click, draft thật, không trigger send từ AI/scheduler, sent audit/message persist.
11. **Out of Scope:** auto-send, marketing/bulk, custom Cc/Bcc, read receipt hoặc bảo đảm exactly-once provider.

## F3 — năm nhóm policy và xác minh (FR04/10)

1. **Objective:** đánh giá xác định, giải thích và chỉ dẫn bước tiếp.
2. **User Story:** nhân viên thấy vấn đề/yêu cầu khác nhau, điều kiện/missing fields và có quyền xử lý ngoại lệ có lý do.
3. **Acceptance Criteria:** đủ năm nhóm; ownership guard; version/snapshot; không để delivered guard chặn not_received; manual không sửa kết quả policy tùy ý.
4. **UI/UX:** policy demo, reason/next action, manual override phân biệt extraction gốc.
5. **API Contract:** complaint_type/requested_action giữ schema gốc, manual review và policy_snapshot mở rộng.
6. **Error Handling:** config sai fail startup; thiếu dữ liệu insufficient_information; unknown order order_not_found; mismatch cần xác minh.
7. **Edge Cases:** hoàn trước giao/sau giao, ngày bất nhất, ranh giới thời hạn, yêu cầu đổi khác ý AI, nhiều lý do trong email.
8. **UI States:** chưa đánh giá/đã đánh giá/thiếu thông tin/manual corrected/provider failed.
9. **Test Cases:** AC03/04/11 và bảng bên dưới, boundary 0/2/7/8 ngày.
10. **DoD:** deterministic tests đủ nhóm, snapshot/version/next action, policy không tự refund hoặc tự reject case.
11. **Out of Scope:** policy admin UI, chính sách pháp lý thật, suy luận ảnh làm bằng chứng gian lận.

### Taxonomy và policy demo-v2

Giữ complaint_type late_delivery/not_received/damaged_item/wrong_item/refund_request/other và requested_action shipping_fee_refund/order_refund/replacement/request_information/other để tương thích SDK schema. Khi hư hỏng + muốn refund: type damaged_item, action order_refund; chỉ type refund_request khi nguyên nhân chưa thuộc bốn nhóm kia. Resolution doanh nghiệp độc lập, theo WORKFLOW.

Guard: thiếu mã → insufficient_information; không tìm thấy → order_not_found; thiếu xác minh → insufficient_information (vẫn được request info). Bất nhất ngày (actual tương lai, actual< purchased nếu có) hoặc thiếu ngày cần dùng → insufficient_information. Email matched/manual verification cho phép rule tiếp tục; AI không xác minh chủ đơn.

| Type/action | Điều kiện demo | Result và bước tiếp |
|---|---|---|
| late_delivery/shipping_fee_refund | delivered actual>expected | eligible_for_review, xem xét hoàn phí |
| late_delivery/shipping_fee_refund | delivered actual<=expected | not_eligible, giải thích ngày giao |
| late_delivery khi chưa giao | chưa đủ bằng chứng hoàn phí | insufficient_information, điều tra giao nhận |
| not_received/any supported action | chưa giao và expected quá >=2 ngày | eligible_for_review, điều tra vận chuyển, không hứa refund |
| not_received | chưa tới grace hoặc DB delivered | insufficient_information, giải thích ETA hoặc kiểm tra giao nhận |
| damaged_item hoặc wrong_item / replacement hoặc order_refund | delivered, nhận complaint trong 7 ngày inclusive, có ảnh khách | eligible_for_review, nhân viên kiểm tra |
| damaged_item hoặc wrong_item | thiếu ảnh hoặc thiếu ngày | insufficient_information, liệt kê cần bổ sung |
| damaged_item hoặc wrong_item | ngoài cửa sổ | not_eligible theo policy demo, cho phép ngoại lệ có lý do |
| refund_request/order_refund | chưa giao/chưa biết nguyên nhân | insufficient_information, hỏi lý do/trạng thái giao |
| refund_request/order_refund | delivered trong 7 ngày | eligible_for_review, xem xét điều kiện hoàn |
| refund_request/order_refund | delivered quá 7 ngày | not_eligible theo demo |
| other/action không hỗ trợ | — | insufficient_information, review thủ công |

Config `policy_version=demo-v2`, `not_received_grace_days=2`, `return_window_days=7`, số nguyên 0..365. Ngày so sánh theo inbound occurred_at ở Asia/Ho_Chi_Minh. Bổ sung không làm mất hạn: đơn/type không đổi dùng ngày khiếu nại đầu tiên của hồ sơ; đổi đơn thì cần manual review, dùng ngày message đầu nêu đơn mới và ghi snapshot. Nếu chưa xác định ngày đó, không tự từ chối vì quá hạn. Số tiền hoàn phí lấy shipping_fee; hoàn đơn chỉ gợi ý số tiền khi total_amount có thật, không tự bịa.

## F4 — đăng nhập, cloud và đồng bộ (FR01/07/08)

1. **Objective:** URL HTTPS dùng được, sync nền không bỏ cuộc trao đổi.
2. **User Story:** nhân viên đăng nhập xem việc mới và biết lần đồng bộ thành công cuối.
3. **Acceptance Criteria:** session/CSRF, OIDC, DB lock, thread follow-up ngoài query ban đầu, data/token/images bền vững.
4. **UI/UX:** login, session expired, connection/last sync/deferred và hàng đợi lỗi; không nói realtime.
5. **API Contract:** auth/integrations/sync/internal và additive counters.
6. **Error Handling:** 401 login, 409 busy, 503 persist last error; không xóa last_success khi sync fail.
7. **Edge Cases:** nhiều instance, token mount readonly, reply chỉ ghi “Đây là ảnh” không có keyword, outbound tự sync.
8. **UI States:** authenticated/expired/unavailable, syncing/success/deferred/failed.
9. **Test Cases:** AC02/07/10/12, follow-up không keyword và unique outgoing ID.
10. **DoD:** Cloud Run thật, SQL/Storage private, Scheduler lịch thật, restart và auth checks đạt.
11. **Out of Scope:** push realtime, SSO, self-service OAuth onboarding và distributed rate limit production.

## F5 — dữ liệu kiểm thử và nghiệm thu sản phẩm (FR09)

1. **Objective:** kiểm chứng đủ sáu hạng mục bằng fixtures lặp được, không task chuẩn bị trình bày.
2. **User Story:** mỗi fullstack có factories phần mình và nhóm chạy full-loop bổ sung, phản hồi, đóng.
3. **Acceptance Criteria:** CPDEMO001–005, mismatch/unknown/missing/manual/one-side, dates tương đối, seed hai lần không trùng.
4. **UI/UX:** dữ liệu kiểm thử rõ, không nút public reset/seed; evidence live không lẫn fixture.
5. **API Contract:** dùng API nghiệp vụ, seed là script/job riêng.
6. **Error Handling:** env email thiếu báo lỗi, không tự dùng email khách thật.
7. **Edge Cases:** ngày kiểm thử khác, seed cũ, query không match, closed nhận reply mới.
8. **UI States:** populated fixtures chỉ development; cloud dữ liệu persist thật.
9. **Test Cases:** AC01–AC12, đặc biệt ca tuần hoàn AC02.
10. **DoD:** release checklist đầy đủ, bảng bằng chứng timestamp/revision/provider, seed repeat test; không slide/diễn tập.
11. **Out of Scope:** benchmark độ chính xác quy mô lớn, tự gửi hàng loạt hoặc xóa mailbox.

## F6 — bằng chứng ảnh (FR06)

1. **Objective:** nhận xét sản phẩm/tình trạng và giới hạn quan sát để hỗ trợ người duyệt.
2. **User Story:** xem ảnh đơn và khách; thiếu ảnh gốc vẫn phân tích ảnh khách được.
3. **Acceptance Criteria:** đúng nguồn message/order, private, validate MIME/bytes, mode one/two side, kết quả Gemini schema validated.
4. **UI/UX:** hai cột khi đủ ảnh; một phía nêu “Chưa có ảnh đối chiếu”; limitations/missing evidence, không nhãn gian lận.
5. **API Contract:** evidence GET/analyze/content; version và DTO theo API.
6. **Error Handling:** không ảnh 422; một phía không lỗi; timeout persist failed không khóa text/manual.
7. **Edge Cases:** góc/ánh sáng khác, ảnh đóng gói không chứng minh tình trạng lúc nhận, ảnh độc hại/trùng/quá lớn.
8. **UI States:** no images/single side/ready/pending/completed/failed/inconclusive.
9. **Test Cases:** AC02/09, decode/limit/private content, prompt injection, stale snapshot.
10. **DoD:** một comparison live và single-side scenario, ảnh không public, kết quả không tự quyết định.
11. **Out of Scope:** video/forensic/fraud score, URL arbitrary, upload UI.

## Owner theo phần fullstack

F1 decisions/lifecycle C + A conversation/core + B manual; F2 C tự UI/API/Gmail; F3 B tự UI/API/policy/text; F4 A tự auth/UI/cloud/sync, B/C dùng real auth ở router own; F5 fixtures domain trong BASE/own tests và ALL1, không vai trò demo; F6 B tự UI/API/ảnh/GCS/Gemini, A truyền raw inbound qua port. Xem TASK FS và SHARED_CONTRACTS, không dùng phân tầng cũ để chờ người khác làm hộ.
