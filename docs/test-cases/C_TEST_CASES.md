# Test cases C fullstack — Resolution + Communication

**27 cases**, phân công v3; tất cả vẫn NOT_RUN. Nguồn: [task C](../tasks/C_RESOLUTION.md), [shared contracts](../SHARED_CONTRACTS.md), [workflow](../WORKFLOW.md), [API](../API_SPECIFICATION.md), [testing](../TESTING_GUIDELINES.md), [AC](../ACCEPTANCE_MATRIX.md).

## Cách dùng

- Mỗi người kiểm UI/API/DB phần mình, không đọc file này như nhiệm vụ chỉ backend/frontend/Google. Phụ thuộc runtime chưa có dùng BASE contract doubles trong tests/dev, không production.
- MERGE trước ghép task; RELEASE trên bản tích hợp trước phát hành. Cả hai bắt buộc, không đổi kỳ vọng để code sai thành PASS.
- Mỗi case độc lập; mọi biến thể cần kết quả. Ghi evidence/revision/reviewer; thiếu dịch vụ là BLOCKED, chưa chạy là NOT_RUN.
- Có thể dùng chung live evidence khi đúng revision và đủ quan sát; không gửi nhiều thư thật chỉ để tăng số test. Fault injection chỉ mocks/DB thử. Live cần task và mailbox nhóm kiểm soát.
- Dòng “Mã cũ” ngay trong mỗi case giữ đối chiếu lịch sử; báo cáo mới dùng ID FS. Không có nhiệm vụ thuyết trình trong các case này.

## FS-C1

### FS-C1-T01 — Vòng yêu cầu bổ sung và quyết định mới

- **Task / yêu cầu / AC:** FS-C1; FR02/FR03; AC02.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/PostgreSQL; Google mock.
- **Điều kiện / dữ liệu:** Hồ sơ damaged có order, chưa ảnh; inbound giả cùng thread chuẩn bị.
- **Các bước:** Request information có missing_fields; complete send mock; ingest email bổ sung; tạo approve replacement mới.
- **Kết quả mong đợi:** waiting_customer chỉ sau sent; inbound về needs_review; decision thứ hai lưu được; hai decisions/messages/audit cùng hồ sơ, không xóa lịch sử.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A2-T01.
- **Trạng thái:** NOT_RUN.

### FS-C1-T02 — Reject, note và action-resolution

- **Task / yêu cầu / AC:** FS-C1; FR03/FR11; AC01/AC06.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/PostgreSQL; Google mock.
- **Điều kiện / dữ liệu:** Complaint xác nhận, chưa quyết định.
- **Các bước:** Thử note rỗng, approve+decline, request_information không missing_fields; sau đó reject+decline hợp lệ và complete send.
- **Kết quả mong đợi:** Input sai bị từ chối không audit thành công; reject hợp lệ append event; chỉ sau sent mới resolved và có thể close, không tạo fulfillment giả.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A2-T03.
- **Trạng thái:** NOT_RUN.

### FS-C1-T03 — Hai quyết định cùng phiên bản

- **Task / yêu cầu / AC:** FS-C1; FR03; AC06.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** PostgreSQL concurrency/API.
- **Điều kiện / dữ liệu:** Hai connection độc lập đọc cùng case_version; barrier đồng bộ.
- **Các bước:** Gửi hai decision khác nhau đồng thời cùng expected_case_version; kiểm rows/audit/version sau commit.
- **Kết quả mong đợi:** Một thành công, một 409 stale_version; chỉ một decision được chấp nhận từ version đó; không hai current decision hoặc audit mồ côi.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A2-T04.
- **Trạng thái:** NOT_RUN.

### FS-C1-T04 — Thay quyết định và reset phương án

- **Task / yêu cầu / AC:** FS-C1; FR03/FR11; AC06/AC07.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/PostgreSQL.
- **Điều kiện / dữ liệu:** Latest approve đã gửi/thực hiện; có history cũ.
- **Các bước:** Mở review, tạo decision thay thế có lý do; thử gửi reply decision cũ; đọc snapshots và fulfillment hiện hành.
- **Kết quả mong đợi:** Decision mới là current; reply cũ không gửi lại; fulfillment hiện hành theo quyết định mới, kết quả thực hiện cũ vẫn còn trong audit, không tự đảo giao dịch.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A2-T06.
- **Trạng thái:** NOT_RUN.

### FS-C1-T05 — Decision validation và nhiều vòng

- **Task / yêu cầu / AC:** FS-C1; FR03; AC01/AC02.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Damaged case needs_review, có và chưa có ownership theo fixture.
- **Các bước:** Chọn approve thiếu resolution/note; request info thiếu missing fields; submit hợp lệ; nhận inbound rồi quyết định lần hai.
- **Kết quả mong đợi:** Chặn input thiếu, gửi action/resolution/version đúng; không khóa vĩnh viễn sau request info; history giữ cả hai decision; approve không phát request send.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B2-T01.
- **Trạng thái:** NOT_RUN.

### FS-C1-T06 — Conflict giữ input và lấy context mới

- **Task / yêu cầu / AC:** FS-C1; FR03/FR10; AC06.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Decision note hoặc manual input đang nhập, case_version cũ.
- **Các bước:** Submit và trả 409 stale_version; fetch detail mới có inbound/decision khác.
- **Kết quả mong đợi:** Giữ input để xem lại, hiện thay đổi; không tự resubmit phiên bản mới hoặc mất note; người dùng chủ động xác nhận lần tiếp theo.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B2-T04.
- **Trạng thái:** NOT_RUN.

## FS-C2

### FS-C2-T01 — Prepare, edit, save và preview nội dung cuối

- **Task / yêu cầu / AC:** FS-C2; FR05; AC05.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Case có current decision, chưa reply.
- **Các bước:** Prepare AI/manual; sửa body; thử gửi khi unsaved; save; mở preview; hủy confirmation.
- **Kết quả mong đợi:** Prepare không gọi draft/send; unsaved không gửi; preview đúng recipient/subject/body đã lưu/revision; hủy không side effect; AI lỗi cho manual.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B3-T01.
- **Trạng thái:** NOT_RUN.

### FS-C2-T02 — Stale vì inbound, revision hoặc decision mới

- **Task / yêu cầu / AC:** FS-C2; FR05; AC06.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Reply prepared hoặc draft_saved đang mở.
- **Các bước:** Trả detail mới có inbound; thử send; review-context cùng decision; sau đó fixture thay decision/order.
- **Kết quả mong đợi:** Giữ body/cảnh báo stale; request bị chặn hoặc 409 trước send; review rõ rồi mới dùng; decision mới cần reply mới, không sửa decision_id reply cũ.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B3-T04.
- **Trạng thái:** NOT_RUN.

### FS-C2-T03 — Lỗi lưu body không gửi nội dung cũ

- **Task / yêu cầu / AC:** FS-C2; FR05; AC05/AC06.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Có body saved v1, sửa v2 nhưng PATCH trả lỗi.
- **Các bước:** Bấm lưu rồi thử preview/send; thử session expired giữa save và send.
- **Kết quả mong đợi:** Giữ v2 như unsaved, không gửi v1 âm thầm hoặc nói v2 đã lưu; lỗi/expired không replay send; To/subject readonly.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B3-T06.
- **Trạng thái:** NOT_RUN.

### FS-C2-T04 — Prepare AI/manual không side effect Gmail

- **Task / yêu cầu / AC:** FS-C2; FR05/FR10; AC04/AC05.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** unit/mock Google/API.
- **Điều kiện / dữ liệu:** Decision hiện hành; Gmail spy; ownership mismatch cho request-info fixture.
- **Các bước:** Prepare AI; lặp prepare; inject provider failure rồi prepare manual; inspect prompt trong fixture kiểm thử riêng.
- **Kết quả mong đợi:** Một reply/decision, chưa draft/send; manual dùng được; không bịa completed refund; khi chưa xác minh prompt không nhận PII đơn nội bộ, credentials không vào prompt/log.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C3-T01.
- **Trạng thái:** NOT_RUN.

## FS-C3

### FS-C3-T01 — Reserve, version và idempotency

- **Task / yêu cầu / AC:** FS-C3; FR05; AC06/AC08.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/PostgreSQL; Gmail call spy.
- **Điều kiện / dữ liệu:** Reply prepared ở case/revision hiện hành, hai request đồng thời.
- **Các bước:** Reserve cùng key/payload; thử key reuse khác payload; thử expected_case_version/reply_revision cũ.
- **Kết quả mong đợi:** Tối đa một active operation và một dispatch; key conflict 409; stale bị chặn trước Gmail; reply sent không được dispatch lại bằng key mới.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A5-T03.
- **Trạng thái:** NOT_RUN.

### FS-C3-T02 — Inbound đến giữa reserve và completion

- **Task / yêu cầu / AC:** FS-C3; FR02/FR05; AC06.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** PostgreSQL concurrency; network barrier.
- **Điều kiện / dữ liệu:** Send reserved, Gmail mock đang chờ, latest inbound đã chụp.
- **Các bước:** Ingest inbound mới; cho Gmail trả success; complete send và đọc case.
- **Kết quả mong đợi:** Sent ID/outbound/audit được persist một lần; case giữ needs_review, không bị completion chuyển chờ thực hiện/closed đè thư mới; concurrent_inbound được ghi nhận.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A5-T04.
- **Trạng thái:** NOT_RUN.

### FS-C3-T03 — Success ngoài DB và recovery unknown

- **Task / yêu cầu / AC:** FS-C3; FR05; AC08.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** PostgreSQL fault injection; Google mock.
- **Điều kiện / dữ liệu:** Gmail mock success nhưng commit completion lỗi hoặc worker chết sau dispatch.
- **Các bước:** Gây lỗi; phục hồi DB/process; tiến clock quá 5 phút; GET/recovery rồi retry intent.
- **Kết quả mong đợi:** sending/draft_saving chuyển unknown theo rule; không auto resend; reconcile có thể bổ sung kết quả với audit, không xóa quyết định/body.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A5-T05.
- **Trạng thái:** NOT_RUN.

### FS-C3-T04 — Nhân viên xác nhận send và double click

- **Task / yêu cầu / AC:** FS-C3; FR05; AC01/AC08.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures/call counter.
- **Điều kiện / dữ liệu:** Reply hiện hành đã save, không stale.
- **Các bước:** Bấm Gửi và xác nhận; double click khi request đang chờ; trả sent và reload.
- **Kết quả mong đợi:** Chỉ một intent send có confirmed=true/key/version/revision đúng; nút khóa; sent hiển thị Gmail ID/trạng thái đúng, không nói khách đã đọc; không nút gửi lại thư sent.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B3-T02.
- **Trạng thái:** NOT_RUN.

### FS-C3-T05 — Save draft, sửa local và external conflict

- **Task / yêu cầu / AC:** FS-C3; FR05; AC05.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Reply draft_saved, có remote hash fixture.
- **Các bước:** Sửa/save local; save draft hoặc send; trả external_draft_changed; hiển thị hai bản, chọn giữ local sau review; trả conflict lần hai với hash mới.
- **Kết quả mong đợi:** Draft không đổi workflow sang chờ khách; local edit không tự tạo draft thứ hai; có preview local/remote và expected_external_hash; không tự ghi đè/hash cũ khi remote đổi tiếp.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B3-T03.
- **Trạng thái:** NOT_RUN.

### FS-C3-T06 — Unknown, failed và polling có giới hạn

- **Task / yêu cầu / AC:** FS-C3; FR05; AC08.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures/fake timers.
- **Điều kiện / dữ liệu:** Reply sending rồi response timeout/unknown; fixture failed chắc chắn riêng.
- **Các bước:** Poll theo timer 3s, tiến quá 60s; reload; thử các nút retry; trả sent muộn qua refresh.
- **Kết quả mong đợi:** Không polling vô hạn, không auto resend; unknown giữ cảnh báo/khóa retry mù; failed không giả sent, retry cần intent người dùng; refresh hiển thị kết quả persist.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B3-T05.
- **Trạng thái:** NOT_RUN.

### FS-C3-T07 — OAuth và quyền Gmail

- **Task / yêu cầu / AC:** FS-C3; FR02/FR05; AC05/AC10.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** Google live metadata/read.
- **Điều kiện / dữ liệu:** Mailbox và OAuth test user nhóm kiểm soát; token không in ra output.
- **Các bước:** Kiểm consent/scopes readonly+compose và đọc một email test; đối chiếu mailbox với GMAIL_ACCOUNT_EMAIL.
- **Kết quả mong đợi:** Đúng mailbox, token đủ phạm vi; readonly-only báo cần consent lại; không test send tới khách, không commit/in token, chưa coi kiểm scope là đã gửi thành công.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C0-T02.
- **Trạng thái:** NOT_RUN.

### FS-C3-T08 — Gửi trực tiếp đúng nội dung và thread

- **Task / yêu cầu / AC:** FS-C3; FR05; AC01/AC05.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** Gmail controlled live + DB/browser.
- **Điều kiện / dữ liệu:** Reply saved hiện hành, chưa Gmail draft; recipient là mailbox nhóm, preview đã kiểm.
- **Các bước:** Nhân viên xác nhận send; kiểm request MIME và inbox controlled/thread; sync lại.
- **Kết quả mong đợi:** Gọi messages.send một lần, đúng body cuối/To/subject/headers, không Cc/Bcc tự thêm; sent ID/audit/outbound persist, không nhân đôi khi sync; không claim read receipt.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C3-T02.
- **Trạng thái:** NOT_RUN.

### FS-C3-T09 — Draft thật, chỉnh local rồi gửi

- **Task / yêu cầu / AC:** FS-C3; FR05; AC05.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** Gmail controlled live + DB/browser.
- **Điều kiện / dữ liệu:** Reply saved, approved/request-info decision hợp lệ, chưa remote edits.
- **Các bước:** Lưu draft, kiểm Gmail; sửa body local/save; gửi sau preview; đối chiếu email received và call path.
- **Kết quả mong đợi:** Draft thật gắn thread; local sửa không tự tạo thêm draft; update draft bằng bản cuối rồi drafts.send, không gọi thêm messages.send; body đến khách đúng nội dung xác nhận.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C3-T03.
- **Trạng thái:** NOT_RUN.

### FS-C3-T10 — Remote draft sửa, xóa hoặc gửi ngoài app

- **Task / yêu cầu / AC:** FS-C3; FR05; AC05/AC08.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** mock Gmail/API/PostgreSQL.
- **Điều kiện / dữ liệu:** Reply draft_saved và hash trước; local edit riêng đã lưu.
- **Các bước:** Trả remote hash khác, thử save/send; review giữ local với expected hash; remote đổi tiếp; biến thể draft missing/external sent.
- **Kết quả mong đợi:** Remote edit 409 external_draft_changed, không nhầm local edit là remote edit; hash đổi lại phải review tiếp; missing/external sent → unknown/reconcile, không tự create/send bản thay.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C3-T04.
- **Trạng thái:** NOT_RUN.

### FS-C3-T11 — Double click, idempotency và explicit rejection

- **Task / yêu cầu / AC:** FS-C3; FR05; AC08.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** mock Gmail/API/PostgreSQL concurrency.
- **Điều kiện / dữ liệu:** Hai send requests cùng key/payload; provider spy; fixture lỗi quyền rõ.
- **Các bước:** Gửi đồng thời/retry cùng key; key khác cho reply sent; key reuse payload khác; Gmail từ chối chắc chắn.
- **Kết quả mong đợi:** Tối đa một dispatch; repeated sent trả kết quả không send; key conflict409; lỗi rõ → failed giữ body/decision, không auto retry SDK; không coi mọi lỗi là unknown hoặc mọi timeout là failed chắc chắn.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C3-T05.
- **Trạng thái:** NOT_RUN.

### FS-C3-T12 — Timeout/crash/DB failure và reconcile

- **Task / yêu cầu / AC:** FS-C3; FR05; AC08.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** fault injection/mock Gmail/PostgreSQL/mock clock.
- **Điều kiện / dữ liệu:** Provider có thể đã tạo/gửi, DB commit lỗi hoặc process chết; có fixtures match/no-match/multiple-match.
- **Các bước:** Inject failure sau dispatch; phục hồi và GET sau5 phút; chạy reconcile CLI trên từng fixture; gọi retry intent.
- **Kết quả mong đợi:** unknown không auto resend/reset; match chắc chắn persist đúng ID/audit; không match/nhiều match giữ unknown; script không gửi thư hoặc tự kết luận chưa gửi chỉ vì search trống.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C3-T06.
- **Trạng thái:** NOT_RUN.

### FS-C3-T13 — Không gửi do AI/scheduler hoặc input giả

- **Task / yêu cầu / AC:** FS-C3; FR01/FR05; AC06/AC08/AC10.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/mock Gmail spies.
- **Điều kiện / dữ liệu:** Có reply; fixtures stale context, stale revision, decision khác, missing confirmed, anonymous/bad CSRF.
- **Các bước:** Thử các request sai; chạy prepare/sync/Scheduler; thử recipient/header injection thay payload client.
- **Kết quả mong đợi:** Không có send call; server không tin actor/To/custom headers client; stale/busy/state bị chặn theo contract, chỉ flow authenticated confirmed current revision mới dispatch.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C3-T07.
- **Trạng thái:** NOT_RUN.

## FS-C4

### FS-C4-T01 — Approve, fulfillment và close

- **Task / yêu cầu / AC:** FS-C4; FR03/FR11; AC01.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/PostgreSQL; Google mock.
- **Điều kiện / dữ liệu:** F-LATE đã xác minh và policy hợp lệ.
- **Các bước:** Approve; thử close; complete send; thử close trước fulfillment; ghi fulfillment; close rồi reload.
- **Kết quả mong đợi:** Approve chưa closed; sent ở waiting_fulfillment; không close sớm; fulfillment completed đưa resolved, close cuối được; không gọi payment/refund API.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A2-T02.
- **Trạng thái:** NOT_RUN.

### FS-C4-T02 — Đóng, mở lại và outbound

- **Task / yêu cầu / AC:** FS-C4; FR02/FR11; AC07.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/PostgreSQL.
- **Điều kiện / dữ liệu:** Case closed có sent history, prepared inbound/outbound IDs.
- **Các bước:** Thử sửa/decision khi closed; ingest outbound; ingest inbound mới; ingest lại cùng Gmail ID; reopen thủ công case khác có note.
- **Kết quả mong đợi:** Closed chặn mutation; outbound không reopen; inbound mở lại và tăng version đúng một lần; history giữ; manual reopen có audit.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A2-T05.
- **Trạng thái:** NOT_RUN.

### FS-C4-T03 — Fulfillment, close và reopen

- **Task / yêu cầu / AC:** FS-C4; FR11; AC01/AC07.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Fixture các trạng thái approved-unsent/sent-waiting/resolved/closed.
- **Các bước:** Quan sát nút; thử close sớm; ghi nhận thực hiện ngoài app; close/reload/reopen có note.
- **Kết quả mong đợi:** Không đóng chỉ vì approve/sent; fulfillment ghi là thao tác bên ngoài, không thực hiện payment; nút đúng điều kiện, timeline/audit hiện; reopen quay needs_review.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B2-T03.
- **Trạng thái:** NOT_RUN.

### FS-C4-T04 — Browser tích hợp và không mock trên Cloud Run

- **Task / yêu cầu / AC:** FS-C4; FR02/FR05/FR09; AC01/AC02/AC05.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** browser + real backend/cloud.
- **Điều kiện / dữ liệu:** Revision cuối, API/DB thật, controlled dataset; không intercept business API.
- **Các bước:** Chạy build/browser regression; mở Network kiểm requests; đi vòng request info → bổ sung → decision → send controlled theo task live.
- **Kết quả mong đợi:** Build/browser đạt; bản cloud dùng API thật, không fixture fallback khi lỗi; ảnh/live Gmail được C xác nhận, không chỉ screenshot fixture.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B5-T02.
- **Trạng thái:** NOT_RUN.

## Bàn giao C

Đủ test bắt buộc và regression theo domain mới đề nghị REVIEW; reviewer xác nhận VERIFIED theo TESTING_GUIDELINES. ALL1 còn cần AC01–AC12 trên Cloud Run. Mock UI/DB không chứng minh Gmail/Gemini/cloud thật.
