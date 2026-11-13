# Test cases B fullstack — Assessment + Evidence

**19 cases**, phân công v3; tất cả vẫn NOT_RUN. Nguồn: [task B](../tasks/B_ASSESSMENT.md), [shared contracts](../SHARED_CONTRACTS.md), [workflow](../WORKFLOW.md), [API](../API_SPECIFICATION.md), [testing](../TESTING_GUIDELINES.md), [AC](../ACCEPTANCE_MATRIX.md).

## Cách dùng

- Mỗi người kiểm UI/API/DB phần mình, không đọc file này như nhiệm vụ chỉ backend/frontend/Google. Phụ thuộc runtime chưa có dùng BASE contract doubles trong tests/dev, không production.
- MERGE trước ghép task; RELEASE trên bản tích hợp trước phát hành. Cả hai bắt buộc, không đổi kỳ vọng để code sai thành PASS.
- Mỗi case độc lập; mọi biến thể cần kết quả. Ghi evidence/revision/reviewer; thiếu dịch vụ là BLOCKED, chưa chạy là NOT_RUN.
- Có thể dùng chung live evidence khi đúng revision và đủ quan sát; không gửi nhiều thư thật chỉ để tăng số test. Fault injection chỉ mocks/DB thử. Live cần task và mailbox nhóm kiểm soát.
- Dòng “Mã cũ” ngay trong mỗi case giữ đối chiếu lịch sử; báo cáo mới dùng ID FS. Không có nhiệm vụ thuyết trình trong các case này.

## FS-B1

### FS-B1-T01 — Sai người gửi và xác minh thủ công

- **Task / yêu cầu / AC:** FS-B1; FR04/FR10; AC03.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/PostgreSQL.
- **Điều kiện / dữ liệu:** Order owner khác From; staff có căn cứ xác minh giả lập.
- **Các bước:** Thử approve trước xác minh; request information; xác minh với reason; approve; đổi order qua review.
- **Kết quả mong đợi:** Approve ban đầu bị chặn; request info được; xác minh lưu actor/reason; approve sau đó được; đổi order reset ownership và current decision, history giữ.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A3-T03.
- **Trạng thái:** NOT_RUN.

### FS-B1-T02 — Đính chính làm quyết định cũ mất hiệu lực

- **Task / yêu cầu / AC:** FS-B1; FR03/FR10; AC04/AC06.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/PostgreSQL.
- **Điều kiện / dữ liệu:** Case có current decision và reply prepared.
- **Các bước:** PATCH đổi order/type/requested_action/ownership từng biến thể; thử review-context/gửi reply cũ; thử acknowledge banner không đổi dữ liệu trên fixture khác.
- **Kết quả mong đợi:** Thay dữ liệu trọng yếu reset current_decision_id, needs_review và cần decision/reply mới; acknowledge thuần không tự hủy decision; mọi thay đổi có before/after/note.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A3-T06.
- **Trạng thái:** NOT_RUN.

### FS-B1-T03 — Manual correction và xác minh

- **Task / yêu cầu / AC:** FS-B1; FR10; AC03/AC04.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** AI failed hoặc wrong order; sender mismatch.
- **Các bước:** Sửa order/type/action có note; xác minh với reason; đổi order; thử approve trước và sau xác minh.
- **Kết quả mong đợi:** AI lỗi vẫn dùng manual được; original và employee correction phân biệt; approval guard phản ánh server; đổi đơn cảnh báo/reset verification/current decision, không giả success nếu PATCH lỗi.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B2-T02.
- **Trạng thái:** NOT_RUN.

## FS-B2

### FS-B2-T01 — Năm policy và taxonomy

- **Task / yêu cầu / AC:** FS-B2; FR04; AC11.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** parameterized unit/PostgreSQL.
- **Điều kiện / dữ liệu:** Năm đơn CPDEMO và config demo-v2, ownership hợp lệ.
- **Các bước:** Chạy late+shipping refund, not_received quá grace, damaged+order refund, wrong+replacement, refund_request sau giao; thêm other.
- **Kết quả mong đợi:** Năm nhóm theo FEATURE_SPECIFICATION, reason/missing_fields/next_action/version persist; damaged+refund vẫn type damaged_item, không bị đổi thành refund_request chỉ vì muốn hoàn tiền.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A3-T01.
- **Trạng thái:** NOT_RUN.

### FS-B2-T02 — Ranh giới thời hạn và ngày thiếu

- **Task / yêu cầu / AC:** FS-B2; FR04; AC11.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** parameterized unit/PostgreSQL.
- **Điều kiện / dữ liệu:** D0=2026-11-14, timezone Asia/Ho_Chi_Minh.
- **Các bước:** Not_received quá hạn 1 và 2 ngày; return ngày 7 và 8; thiếu expected/actual; actual tương lai hoặc trước purchased; thiếu order ID/ID không tồn tại.
- **Kết quả mong đợi:** Kết quả theo policy demo-v2: grace 2 đủ điều kiện điều tra; return 7 inclusive, 8 ngoài cửa sổ; thiếu/bất nhất không crash hay tự approve; phân biệt insufficient_information và order_not_found.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A3-T02.
- **Trạng thái:** NOT_RUN.

### FS-B2-T03 — Probe text và Gemini ảnh

- **Task / yêu cầu / AC:** FS-B2; FR04/FR06; AC04/AC09.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** Google live synthetic probe.
- **Điều kiện / dữ liệu:** Key/model cấu hình riêng, ảnh và nội dung giả, không PII.
- **Các bước:** Gọi text structured output và Gemini image với schema; ghi model/provider/duration/error code sanitized.
- **Kết quả mong đợi:** Output validate hoặc báo quota/timeout/model access rõ; không đổi provider âm thầm/giả Groq text là Gemini ảnh; thiếu image capability vẫn BLOCKED phần ảnh.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C0-T03.
- **Trạng thái:** NOT_RUN.

## FS-B3

### FS-B3-T01 — Seed ảnh hai pha và retry

- **Task / yêu cầu / AC:** FS-B3; FR06/FR09; AC09/AC11.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** PostgreSQL + manifest Storage FS-B3.
- **Điều kiện / dữ liệu:** Orders pha1 tồn tại, manifest ảnh giả do FS-B3 tạo.
- **Các bước:** Attach metadata pha2 hai lần; thử manifest gắn nhầm owner/không tồn tại; đọc evidence của order đúng.
- **Kết quả mong đợi:** Ảnh hợp lệ gắn đúng FK và dedupe; manifest sai không sinh asset mồ côi; thiếu cloud manifest ghi BLOCKED pha2, không chặn kiểm tra pha1 bằng fake ảnh.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A4-T03.
- **Trạng thái:** NOT_RUN.

### FS-B3-T02 — Hai phía, một phía và không ảnh

- **Task / yêu cầu / AC:** FS-B3; FR06; AC09.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Fixtures comparison/single_side/no assets với labels nguồn.
- **Các bước:** Mở evidence, chuyển giữa fixtures; chạy analyze khi một phía; xem observations/limitations.
- **Kết quả mong đợi:** Nguồn đúng, one-side nói chưa có ảnh đối chiếu/inconclusive, không giả comparison; không ảnh có hướng dẫn; không nhãn gian lận hoặc auto reject.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B4-T01.
- **Trạng thái:** NOT_RUN.

### FS-B3-T03 — Ảnh loading/lỗi và provider fail

- **Task / yêu cầu / AC:** FS-B3; FR06; AC09.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Image content trả chậm/404; analysis pending hoặc failed.
- **Các bước:** Mở panel, simulate broken image và Gemini timeout, retry theo user click.
- **Kết quả mong đợi:** Fallback/alt/error từng ảnh rõ; không khóa conversation/manual decision; loading không báo completed giả; retry không bắn lặp khi pending.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B4-T02.
- **Trạng thái:** NOT_RUN.

### FS-B3-T04 — Mobile, keyboard và phóng to

- **Task / yêu cầu / AC:** FS-B3; FR06/NFR04; AC09.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** browser/accessibility manual.
- **Điều kiện / dữ liệu:** Viewport390px và desktop, có ảnh kích thước khác nhau.
- **Các bước:** Dùng Tab/Enter/Escape, phóng to/đóng ảnh, focus quay lại; kiểm scroll/textarea/action trên mobile.
- **Kết quả mong đợi:** Không overflow hoặc overlay che nội dung; labels/alt/focus rõ, không chỉ dùng màu; mọi action cần thiết đi được bằng bàn phím.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B4-T03.
- **Trạng thái:** NOT_RUN.

### FS-B3-T05 — Least privilege và private Storage

- **Task / yêu cầu / AC:** FS-B3; FR06/FR07; AC09/AC12.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** cloud IAM/read checks.
- **Điều kiện / dữ liệu:** Runtime/Scheduler SA và bucket test đúng project.
- **Các bước:** Đọc IAM bindings/bucket policy, thử anonymous đọc object ảnh giả và authenticated API content sau auth được wire.
- **Kết quả mong đợi:** Không Owner/Editor runtime; bucket không public; anonymous bị chặn, API đúng phiên xem được; không biến public bucket thành cách chữa lỗi ảnh.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C1-T03.
- **Trạng thái:** NOT_RUN.

### FS-B3-T06 — MIME/byte/pixel và attachment URL

- **Task / yêu cầu / AC:** FS-B3; FR06; AC09.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** unit/decoder/mock Storage.
- **Điều kiện / dữ liệu:** Ảnh JPEG/PNG hợp lệ, giả MIME/SVG/archive/corrupt, byte5242880 và5242881, pixel20MP và vượt.
- **Các bước:** Decode/upload từng biến thể; email có URL ảnh ngoài; mock downloader spy.
- **Kết quả mong đợi:** Ảnh trong giới hạn decode được; ảnh giả/quá byte/pixel bị chặn bounded; không fetch URL; lỗi ảnh không hủy text/manual, không dùng filename làm object path.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C4-T01.
- **Trạng thái:** NOT_RUN.

### FS-B3-T07 — Nguồn ảnh, dedupe và snapshot lựa chọn

- **Task / yêu cầu / AC:** FS-B3; FR06; AC02/AC09.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** PostgreSQL/mock Storage/Gemini.
- **Điều kiện / dữ liệu:** Ảnh đơn và customer từ nhiều inbound, duplicate sha cùng owner, >2 ảnh/phía.
- **Các bước:** Ingest ảnh lặp; chọn input analyze theo kiến trúc; kiểm asset FK/hash/snapshot và prompt images.
- **Kết quả mong đợi:** Dedupe đúng owner, không gắn ảnh order nhầm customer; tối đa2/phía, selection ổn định từ nguồn quy định; asset_ids persist đúng những ảnh đã gửi AI, không đưa tất cả ảnh vô hạn.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C4-T02.
- **Trạng thái:** NOT_RUN.

### FS-B3-T08 — Gemini comparison thật

- **Task / yêu cầu / AC:** FS-B3; FR06; AC09.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** Gemini live synthetic images + private Storage.
- **Điều kiện / dữ liệu:** Hai phía ảnh giả cùng sản phẩm/tình trạng khác, model image đã probe.
- **Các bước:** Analyze qua API bằng phiên, xem output/model/asset snapshot; mở UI hai phía; thử anonymous content.
- **Kết quả mong đợi:** mode comparison, schema valid và nêu giới hạn/observations; không verdict gian lận/tự quyết định; ảnh private, có model thật chứ không fixture/Groq text giả.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C4-T03.
- **Trạng thái:** NOT_RUN.

### FS-B3-T09 — Một phía và không ảnh

- **Task / yêu cầu / AC:** FS-B3; FR06; AC09.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** mock Gemini/API.
- **Điều kiện / dữ liệu:** Customer-only, order-only và zero-assets fixtures.
- **Các bước:** Analyze từng fixture; inspect response mode/consistency/limitations; kiểm zero-assets call count.
- **Kết quả mong đợi:** Một phía vẫn chạy single_side/inconclusive, nêu thiếu gì; zero-assets422 evidence_missing, không gọi Gemini; không claim đã đối chiếu khi thiếu một phía.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C4-T04.
- **Trạng thái:** NOT_RUN.

### FS-B3-T10 — Pending, output sai, timeout và context mới

- **Task / yêu cầu / AC:** FS-B3; FR06; AC06/AC09.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** mock Gemini/PostgreSQL concurrency/mock clock.
- **Điều kiện / dữ liệu:** Một pending analysis; provider trả invalid schema/timeout hoặc completed sau context mới.
- **Các bước:** Analyze đồng thời; inject schema/timeout; tiến pending quá5 phút; complete chậm rồi kiểm case/reply.
- **Kết quả mong đợi:** Một pending/case; lỗi persist failed không fabricated observations; recovery có retry user; raw snapshot giữ, completion không ghi đè context mới và reply chưa gửi cần review theo workflow.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C4-T05.
- **Trạng thái:** NOT_RUN.

## FS-B4

### FS-B4-T01 — AI lỗi, sửa tay và AI hoàn tất muộn

- **Task / yêu cầu / AC:** FS-B4; FR10; AC04/AC06.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/PostgreSQL; provider mock.
- **Điều kiện / dữ liệu:** Candidate NULL bị timeout, raw message có processing_error; mock AI có barrier.
- **Các bước:** Confirm complaint/manual order/type; reassess không gọi AI; hoàn tất AI cũ hoặc retry với dữ liệu khác.
- **Kết quả mong đợi:** Manual xử lý tiếp được; data_source=manual, raw AI/error gốc giữ; mỗi attempt có text_analysis_runs riêng, failed/stale không bị xóa; late completion giữ output nhưng không apply/current pointer/ghi đè manual override hoặc version mới, applied_case_version=NULL. Kiểm DB06 trong DATABASE_DESIGN.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A3-T04.
- **Trạng thái:** NOT_RUN.

### FS-B4-T02 — Snapshot và ngày khiếu nại đầu

- **Task / yêu cầu / AC:** FS-B4; FR04/FR10; AC11.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** PostgreSQL/unit.
- **Điều kiện / dữ liệu:** Complaint gửi trong ngày 7; ảnh bổ sung ngày 9, cùng đơn/type.
- **Các bước:** Assess lần đầu; ingest ảnh ngày 9 và reassess; thay DB order sau quyết định; đọc assessment_snapshot cũ.
- **Kết quả mong đợi:** Không mất điều kiện chỉ vì bổ sung muộn; dùng ngày khiếu nại đầu đúng đơn; snapshot cũ không đổi theo order hiện tại; thiếu căn cứ ngày không tự từ chối vì quá hạn.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A3-T05.
- **Trạng thái:** NOT_RUN.

### FS-B4-T03 — Dữ liệu kiểm thử và traceability assessment

- **Task / yêu cầu / AC:** FS-B4; FR09; AC01–AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** review/fixture validation.
- **Điều kiện / dữ liệu:** Assessment fixtures trao đổi qua BASE, DEMO_DATE/customer email là biến.
- **Các bước:** Đối chiếu CPDEMO001–005 và ca mismatch/missing/unknown/manual/one-side/reopen với AC; kiểm ảnh giả/email labels.
- **Kết quả mong đợi:** Đủ ca, đúng field/relative dates/nguồn ảnh, không PII/credential thật; fixtures tách rõ dữ liệu cloud thật, có task-owner cho từng dependency.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B5-T01.
- **Trạng thái:** NOT_RUN.

## Bàn giao B

Đủ test bắt buộc và regression theo domain mới đề nghị REVIEW; reviewer xác nhận VERIFIED theo TESTING_GUIDELINES. ALL1 còn cần AC01–AC12 trên Cloud Run. Mock UI/DB không chứng minh Gmail/Gemini/cloud thật.
