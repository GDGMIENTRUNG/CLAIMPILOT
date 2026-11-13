# Test cases A fullstack — Workspace + Cloud Run

**32 cases**, phân công v3; tất cả vẫn NOT_RUN. Nguồn: [task A](../tasks/A_WORKSPACE.md), [shared contracts](../SHARED_CONTRACTS.md), [workflow](../WORKFLOW.md), [API](../API_SPECIFICATION.md), [testing](../TESTING_GUIDELINES.md), [AC](../ACCEPTANCE_MATRIX.md).

## Cách dùng

- Mỗi người kiểm UI/API/DB phần mình, không đọc file này như nhiệm vụ chỉ backend/frontend/Google. Phụ thuộc runtime chưa có dùng BASE contract doubles trong tests/dev, không production.
- MERGE trước ghép task; RELEASE trên bản tích hợp trước phát hành. Cả hai bắt buộc, không đổi kỳ vọng để code sai thành PASS.
- Mỗi case độc lập; mọi biến thể cần kết quả. Ghi evidence/revision/reviewer; thiếu dịch vụ là BLOCKED, chưa chạy là NOT_RUN.
- Có thể dùng chung live evidence khi đúng revision và đủ quan sát; không gửi nhiều thư thật chỉ để tăng số test. Fault injection chỉ mocks/DB thử. Live cần task và mailbox nhóm kiểm soát.
- Dòng “Mã cũ” ngay trong mỗi case giữ đối chiếu lịch sử; báo cáo mới dùng ID FS. Không có nhiệm vụ thuyết trình trong các case này.

## FS-A1

### FS-A1-T01 — Login thành công và bảo vệ API

- **Task / yêu cầu / AC:** FS-A1; FR01; AC10.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/PostgreSQL.
- **Điều kiện / dữ liệu:** Account staff cấu hình và app chạy local test.
- **Các bước:** Login đúng Origin; gọi me và detail; bỏ cookie gọi detail; đọc cookie attributes trên cấu hình cloud test.
- **Kết quả mong đợi:** Phiên hợp lệ truy cập được; anonymous 401; cookie HttpOnly/SameSite=Lax/Secure cloud; DB chỉ lưu hash, JSON không trả session token/password.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A1-T01.
- **Trạng thái:** NOT_RUN.

### FS-A1-T02 — Sai mật khẩu và giới hạn đăng nhập

- **Task / yêu cầu / AC:** FS-A1; FR01; AC10.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/mock clock.
- **Điều kiện / dữ liệu:** Account test; clock/IP fixture kiểm soát.
- **Các bước:** Login sai nhiều lần cùng IP trong 15 phút; thử lại sau cửa sổ; kiểm tra error/log.
- **Kết quả mong đợi:** Sai thông tin không tạo phiên; giới hạn 5 lần thất bại/15 phút có hiệu lực; lỗi không tiết lộ password/account; không tin IP header giả do client đặt.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A1-T02.
- **Trạng thái:** NOT_RUN.

### FS-A1-T03 — Logout và phiên hết hạn

- **Task / yêu cầu / AC:** FS-A1; FR01; AC10.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/PostgreSQL/mock clock.
- **Điều kiện / dữ liệu:** Một phiên hợp lệ, clock có thể tiến.
- **Các bước:** Logout rồi dùng lại cookie cũ; tạo phiên khác và tiến quá TTL 8h; gọi me/business API.
- **Kết quả mong đợi:** Logout 204 và revoke; token cũ/hết hạn nhận 401; không chỉ xóa cookie ở browser mà server vẫn chấp nhận.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A1-T03.
- **Trạng thái:** NOT_RUN.

### FS-A1-T04 — Origin và CSRF trên mutation

- **Task / yêu cầu / AC:** FS-A1; FR01; AC10.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API.
- **Điều kiện / dữ liệu:** Phiên hợp lệ, biết CSRF test; có counters DB trước.
- **Các bước:** Gọi decision/PATCH review/logout với CSRF thiếu/sai hoặc Origin khác; thử login cross-origin; sau đó gọi đúng thông tin.
- **Kết quả mong đợi:** Request không hợp lệ bị chặn trước mutation; DB/Gmail không side effect; request hợp lệ hoạt động, health vẫn public.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A1-T04.
- **Trạng thái:** NOT_RUN.

### FS-A1-T05 — JSON, PATCH, CSRF và 204

- **Task / yêu cầu / AC:** FS-A1; FR01/FR05; AC05/AC10.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Frontend chạy, intercept API đúng contract; session/CSRF fixture.
- **Các bước:** Gọi GET detail, PATCH body, POST decision/logout; quan sát method/JSON/header và response 204.
- **Kết quả mong đợi:** Payload/enums đúng, mutation có CSRF, 204 không lỗi parse, không session token trong localStorage hoặc frontend bundle.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B0-T01.
- **Trạng thái:** NOT_RUN.

### FS-A1-T06 — Lỗi API và 401 không replay

- **Task / yêu cầu / AC:** FS-A1; FR01/FR05; AC08/AC10.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Composer đang có body chưa gửi.
- **Các bước:** Trả 422 detail array, 503 detail/code, network error và 401 khi mutation; login lại và quan sát requests.
- **Kết quả mong đợi:** UI không crash; thông báo có ích, giữ nội dung khi có thể; 401 về login/giữ route, không tự replay mutation sau login hoặc tự gửi lại.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B0-T02.
- **Trạng thái:** NOT_RUN.

### FS-A1-T07 — Login/logout/expired và deep-link

- **Task / yêu cầu / AC:** FS-A1; FR01; AC10.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** URL có ?case=ID, chưa login.
- **Các bước:** Login, reload me, mở detail, logout; lặp với expired session.
- **Kết quả mong đợi:** Login/expired đúng state/focus, giữ đường dẫn hữu ích; logout bỏ dữ liệu phiên khỏi UI; không hiện hồ sơ cũ như đã authenticated sau lỗi me.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B1-T01.
- **Trạng thái:** NOT_RUN.

## FS-A2

### FS-A2-T01 — Seed lặp và ngày tương đối

- **Task / yêu cầu / AC:** FS-A2; FR09; AC11.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** PostgreSQL/script.
- **Điều kiện / dữ liệu:** DB thử, DEMO_DATE và DEMO_CUSTOMER_EMAIL controlled.
- **Các bước:** Chạy seed pha1 hai lần; kiểm CPDEMO001–005, ngày/shipping/total; đổi DEMO_DATE trên DB thử mới và seed.
- **Kết quả mong đợi:** Không nhân đôi; đủ năm tình huống; ngày tương đối đúng; tổng tiền thiếu không tự bịa; không gửi email hoặc sinh sent event.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A4-T01.
- **Trạng thái:** NOT_RUN.

### FS-A2-T02 — Seed thiếu env và bảo toàn đơn cũ

- **Task / yêu cầu / AC:** FS-A2; FR09; AC11.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** script/PostgreSQL.
- **Điều kiện / dữ liệu:** Có đơn không CPDEMO cần giữ; test bỏ env email.
- **Các bước:** Chạy seed thiếu email; sau đó chạy đủ env; so nội dung/IDs đơn có sẵn.
- **Kết quả mong đợi:** Thiếu email báo lỗi có ích, không lấy email người thật mặc định; đơn cũ giữ nguyên; không truncate/reset volume.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A4-T02.
- **Trạng thái:** NOT_RUN.

### FS-A2-T03 — Queues, lọc và technical candidate

- **Task / yêu cầu / AC:** FS-A2; FR02/FR08; AC07/AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Dataset đủ 5 workflow statuses, candidate NULL failed và non-complaint false.
- **Các bước:** Đổi queue/filter/page; vào technical, mở candidate; quay lại từ detail.
- **Kết quả mong đợi:** Work queue chỉ complaint true, technical thấy candidate lỗi theo contract; false không lẫn; counts/filter đúng, giữ filter/page khi quay lại; empty/no-match tách biệt.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B1-T02.
- **Trạng thái:** NOT_RUN.

### FS-A2-T04 — Conversation và timeline đúng hồ sơ

- **Task / yêu cầu / AC:** FS-A2; FR02/FR03; AC02/AC07.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Một case có 3 inbound, 2 outbound, decisions/audit/ảnh khác thời gian.
- **Các bước:** Mở detail, đọc toàn conversation và timeline; reload; hiển thị email có HTML/script như text.
- **Kết quả mong đợi:** Đúng chiều và thời gian Việt Nam, stable ordering; original email không bị thay bởi latest; không chạy HTML/script; attachments đúng message, không thành nhiều hồ sơ rời.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B1-T03.
- **Trạng thái:** NOT_RUN.

### FS-A2-T05 — MIME Unicode, headers và giới hạn

- **Task / yêu cầu / AC:** FS-A2; FR02; AC02/AC07.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** unit parser/mock Gmail.
- **Điều kiện / dữ liệu:** Fixtures nested MIME/plain/html, tiếng Việt, From/Message-ID/References/thread và raw lỗi/quá cap.
- **Các bước:** Parse từng biến thể; thử script HTML và raw malformed/>25MB decoded; inspect ParsedMessage/error.
- **Kết quả mong đợi:** Text/header/thread/direction/time đúng, không execute HTML; raw vượt giới hạn/lỗi xử lý bounded và báo rõ; không log body hoặc mất saved text có thể đọc an toàn.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C2-T01.
- **Trạng thái:** NOT_RUN.

### FS-A2-T06 — Follow-up không keyword trong thread cũ

- **Task / yêu cầu / AC:** FS-A2; FR02; AC02.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** Gmail controlled live + DB.
- **Điều kiện / dữ liệu:** Một case đã request ảnh và sent; customer mailbox nhóm có quyền gửi theo task.
- **Các bước:** Reply cùng thread chỉ “Tôi gửi ảnh” kèm ảnh, không mã đơn; sync bằng known-thread path ngoài discovery query.
- **Kết quả mong đợi:** Một inbound mới vào case cũ, ảnh gắn đúng message, needs_review và version tăng; quyết định tiếp được; không bắt khách lặp mã/từ khóa.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C2-T02.
- **Trạng thái:** NOT_RUN.

### FS-A2-T07 — Dedupe, outbound và thread khác

- **Task / yêu cầu / AC:** FS-A2; FR02; AC07.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** mock Gmail/PostgreSQL.
- **Điều kiện / dữ liệu:** Fixtures cùng message ID lặp, app sent outbound, new thread cùng order, closed case.
- **Các bước:** Sync hai lần; ingest outbound; ingest new-thread same-order; ingest inbound mới vào closed.
- **Kết quả mong đợi:** Message/outbound không nhân đôi; outbound không reopen/create case; same-order new-thread không auto gộp; inbound mới reopen đúng canonical case.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C2-T03.
- **Trạng thái:** NOT_RUN.

### FS-A2-T08 — Cursor, pagination và deferred qua restart

- **Task / yêu cầu / AC:** FS-A2; FR08; AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** mock Gmail/PostgreSQL/mock clock.
- **Điều kiện / dữ liệu:** Hơn20 known threads và hơn5 inbound mới, discovery nhiều trang; có closed thread và token hết hiệu lực.
- **Các bước:** Sync tới giới hạn; restart app và sync tiếp; giả invalid page token; kiểm cursor/pending IDs/counts.
- **Kết quả mong đợi:** Không quá ngân sách/batch, còn lại persisted deferred; tiếp tục vòng quét không bỏ/lặp vô hạn trang đầu; invalid token reset có dedupe; known thread không bị time-window query loại.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C2-T04.
- **Trạng thái:** NOT_RUN.

### FS-A2-T09 — Non-complaint có nội dung mới và lỗi AI

- **Task / yêu cầu / AC:** FS-A2; FR02/FR10; AC02/AC04/AC07.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** mock Gmail/AI/PostgreSQL.
- **Điều kiện / dữ liệu:** Thread từng false, candidate NULL failed, raw email lưu trước.
- **Các bước:** Append reply mới có complaint; gọi classify; inject timeout và sau đó manual review.
- **Kết quả mong đợi:** Không bỏ thread vĩnh viễn; tri-state được cập nhật theo dữ liệu mới; timeout vẫn giữ message, hiển thị technical queue/manual path, không tạo thành công giả.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C2-T05.
- **Trạng thái:** NOT_RUN.

## FS-A3

### FS-A3-T01 — Baseline và hợp đồng

- **Task / yêu cầu / AC:** FS-A3; FR02/FR07; AC07/AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** review/static.
- **Điều kiện / dữ liệu:** Repo dirty, ba worktree chưa tạo.
- **Các bước:** Đọc git status/diff; kiểm kê schema/DTO/config; đối chiếu API với fixture B và signatures C.
- **Kết quả mong đợi:** Không mất thay đổi sẵn có; ba vai trò dùng cùng baseline đã chốt; fields/enums/nullability thống nhất, không stub giả thành feature hoàn thành.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A0-T01.
- **Trạng thái:** NOT_RUN.

### FS-A3-T02 — Migration database mới

- **Task / yêu cầu / AC:** FS-A3; FR07; AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** PostgreSQL/migration.
- **Điều kiện / dữ liệu:** DB thử trống, env riêng; không dùng DB khách hàng.
- **Các bước:** Chạy heads, upgrade head, current và alembic check; kiểm tra tables/FKs/indexes trong thiết kế.
- **Kết quả mong đợi:** Một head; schema lên được; constraints có thật; ORM không drift; không có credential trong output lưu bằng chứng.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A0-T02.
- **Trạng thái:** NOT_RUN.

### FS-A3-T03 — Backfill dữ liệu cũ và lặp lại

- **Task / yêu cầu / AC:** FS-A3; FR02/FR07; AC07/AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** PostgreSQL/migration.
- **Điều kiện / dữ liệu:** DB thử ở schema cũ, có candidates NULL/false/true và processed cũ; hai legacy rows cùng Gmail thread.
- **Các bước:** Upgrade; backfill; chụp counts/IDs; chạy backfill lại; đọc canonical case.
- **Kết quả mong đợi:** Giữ nội dung/ID cũ và tri-state; một message/Gmail ID, một canonical/thread; không tự tạo quyết định/đã gửi/đã đóng giả; lần hai không nhân đôi.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A0-T03.
- **Trạng thái:** NOT_RUN.

### FS-A3-T04 — Ràng buộc dữ liệu

- **Task / yêu cầu / AC:** FS-A3; FR02/FR03/FR06; AC06/AC09.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** PostgreSQL.
- **Điều kiện / dữ liệu:** DB thử đã migrate.
- **Các bước:** Trong transaction riêng thử insert Gmail ID trùng, asset không owner hoặc hai owner, version âm và hai pending evidence cùng case.
- **Kết quả mong đợi:** Constraint chặn dữ liệu sai; rollback sạch, dữ liệu hợp lệ vẫn lưu được; không chỉ kiểm ở UI.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A0-T04.
- **Trạng thái:** NOT_RUN.

### FS-A3-T05 — Type contract và build

- **Task / yêu cầu / AC:** FS-A3; FR02/FR05; AC05/AC07.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** TypeScript build/static.
- **Điều kiện / dữ liệu:** Fixtures có UUID/int/null, workflow counts, reply envelope và technical candidate.
- **Các bước:** Build; so keys/types fixtures với API spec; thử absent optional/null và các reply status.
- **Kết quả mong đợi:** Build đạt không any để che sai; nullable hiển thị an toàn; không dùng case_status cũ thay workflow_status mới; fixtures không lệch shape backend.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B0-T03.
- **Trạng thái:** NOT_RUN.

### FS-A3-T06 — Kiểm tra phát hành bởi người khác

- **Task / yêu cầu / AC:** FS-A3; FR09; AC01–AC12.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** manual full-loop/review.
- **Điều kiện / dữ liệu:** Revision Cloud Run cần nghiệm thu, release checklist và evidence ba domain có sẵn.
- **Các bước:** Reviewer khác thực hiện release checklist trên revision đã ghi; đối chiếu evidence và mọi assertion, không kiểm tra kỹ năng thuyết trình.
- **Kết quả mong đợi:** Full-loop sản phẩm được người khác kiểm chứng, live/mocked/BLOCKED ghi đúng; không đánh dấu toàn bộ task VERIFIED chỉ vì giao diện hiển thị đẹp hoặc báo cáo tác giả nói đã xong.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B5-T03.
- **Trạng thái:** NOT_RUN.

### FS-A3-T07 — Đúng project, quyền và APIs

- **Task / yêu cầu / AC:** FS-A3; FR07/FR08; AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** cloud read-only preflight.
- **Điều kiện / dữ liệu:** CLI authenticated bằng tài khoản nhóm, project dự kiến được cung cấp riêng.
- **Các bước:** Kiểm active account/project/billing, enabled APIs/quota và quyền Run/SQL/Storage/Secrets/Scheduler/actAs; đối chiếu project nhóm.
- **Kết quả mong đợi:** Đúng project và có quyền cần dùng; thiếu gì ghi BLOCKED cụ thể; không tự đổi project/cấp Owner hoặc tạo tài nguyên trong bài kiểm chỉ đọc.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C0-T01.
- **Trạng thái:** NOT_RUN.

### FS-A3-T08 — Container PORT và SPA/API routing

- **Task / yêu cầu / AC:** FS-A3; FR07; AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** container/local HTTP.
- **Điều kiện / dữ liệu:** Image build từ revision, PORT khác dev default.
- **Các bước:** Start container bind PORT; GET health, frontend/deep-link và /api/unknown; inspect image file list/build inputs.
- **Kết quả mong đợi:** Bind 0.0.0.0 PORT đúng; SPA hoạt động, unknown API JSON404; không mang .env/token/.git/venv/node_modules dev vào image.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C1-T01.
- **Trạng thái:** NOT_RUN.

### FS-A3-T09 — Cloud SQL, Secret mount và token refresh

- **Task / yêu cầu / AC:** FS-A3; FR07; AC12.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** cloud live/synthetic expired-access-token.
- **Điều kiện / dữ liệu:** Runtime SA/project đúng, token refresh hợp lệ trong Secret mount readonly; không revoke token thật để thử.
- **Các bước:** Deploy skeleton; health DB; dùng token fixture access-expired có refresh để đọc controlled email; quan sát readonly mount/log sanitized.
- **Kết quả mong đợi:** SQL kết nối qua cấu hình dự kiến; refresh memory không ghi mount, không lỗi permission; secrets không ở VITE env/response/log hoặc deploy command public.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C1-T02.
- **Trạng thái:** NOT_RUN.

### FS-A3-T10 — Revision mới giữ dữ liệu/token/ảnh

- **Task / yêu cầu / AC:** FS-A3; FR06/FR07; AC09/AC12.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** cloud live smoke.
- **Điều kiện / dữ liệu:** Case có messages/decision/sent ID/ảnh, token secret readonly.
- **Các bước:** Deploy revision mới cùng schema; login lại nếu cần; reload case/evidence, sync/read Gmail.
- **Kết quả mong đợi:** DB/history/IDs/ảnh còn, token tiếp tục dùng được không phụ thuộc local filesystem; không tự send lại operation sau restart.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C5-T03.
- **Trạng thái:** NOT_RUN.

### FS-A3-T11 — Rollback và nghiệm thu cuối

- **Task / yêu cầu / AC:** FS-A3; FR07/FR09; AC01–AC12.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** cloud staging/controlled review.
- **Điều kiện / dữ liệu:** Revision tốt và schema compatibility đã xác minh; người review khác có runbook/evidence.
- **Các bước:** Diễn tập rollback trên môi trường nghiệm thu cô lập: pause scheduler/mutations, chuyển revision compatible rồi resume; đối chiếu AC01–AC12 revision cuối.
- **Kết quả mong đợi:** Không hai writer phiên bản khác/không drop-downgrade DB; dữ liệu giữ; biết revision phục hồi; PASS/FAIL/BLOCKED theo bằng chứng thật, không tự xóa tài nguyên hoặc claim production-ready.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C5-T04.
- **Trạng thái:** NOT_RUN.

## FS-A4

### FS-A4-T01 — Khóa sync/retry khác process

- **Task / yêu cầu / AC:** FS-A4; FR02/FR08; AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** PostgreSQL concurrency/API.
- **Điều kiện / dữ liệu:** Hai app/process dùng cùng DB, Google mocked.
- **Các bước:** Giữ sync lock ở process1; gọi sync/retry/internal ở process2; kết thúc và thử lại.
- **Kết quả mong đợi:** Overlap nhận 409, không thêm call provider; sau release chạy được; không chỉ dùng threading.Lock hoặc max-instances để giả kiểm tra.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A5-T01.
- **Trạng thái:** NOT_RUN.

### FS-A4-T02 — Lỗi vẫn giải phóng khóa và rollback

- **Task / yêu cầu / AC:** FS-A4; FR03/FR08; AC08/AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** PostgreSQL fault injection.
- **Điều kiện / dữ liệu:** Hook mock phát exception ở ingest/assessment/decision.
- **Các bước:** Inject lỗi trong transaction; kiểm message/decision/audit; gọi lại operation sau lỗi.
- **Kết quả mong đợi:** Rollback đúng phạm vi, không audit thành công mồ côi; sync lock được release; saved email trước AI không mất; không giữ transaction khi chờ network.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** A5-T02.
- **Trạng thái:** NOT_RUN.

### FS-A4-T03 — Sync lỗi, deferred và last success

- **Task / yêu cầu / AC:** FS-A4; FR08; AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** browser/API fixtures.
- **Điều kiện / dữ liệu:** Có last_success cũ, deferred_count>0.
- **Các bước:** Sync loading; trả success có deferred; lần sau trả integration error; reload status.
- **Kết quả mong đợi:** Chặn bấm sync lặp trong loading; không nói realtime/đã xử lý hết khi deferred; lỗi không cập nhật last_success giả; hiển thị lần thành công cũ và lỗi mới rõ.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** B1-T04.
- **Trạng thái:** NOT_RUN.

### FS-A4-T04 — Scheduler OIDC đúng và sai

- **Task / yêu cầu / AC:** FS-A4; FR01/FR08; AC10/AC12.
- **Mốc bắt buộc:** MERGE.
- **Loại kiểm tra:** API/mock signed token verifier.
- **Điều kiện / dữ liệu:** Internal route public network, verifier test double hoặc token ký hợp lệ test; server không decode-only.
- **Các bước:** Thử thiếu token, sai signature/issuer/audience/email/email_verified; token đúng allowlist; thử cookie staff thay OIDC.
- **Kết quả mong đợi:** Sai token401/403 không sync; đúng token chỉ sync, không send; staff cookie không thay OIDC; test xác nhận verifier signature thực sự được gọi.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C5-T01.
- **Trạng thái:** NOT_RUN.

### FS-A4-T05 — Cloud migration, Scheduler và last sync

- **Task / yêu cầu / AC:** FS-A4; FR07/FR08; AC12.
- **Mốc bắt buộc:** RELEASE.
- **Loại kiểm tra:** cloud live logs/DB/browser.
- **Điều kiện / dữ liệu:** Image revision cuối, migration/backfill đã test, correct SA/env.
- **Các bước:** Chạy migration job exit0/single head; deploy; Scheduler run-now và đợi lượt5 phút; xem status/deferred/log.
- **Kết quả mong đợi:** HTTPS/API/auth đúng; có invocation thật không chỉ job-created; SQL persist; last_attempt/last_success/error đúng semantics, không log secret; pending backlog không bị báo đã xử lý hết.
- **Kết quả thực tế:** Chưa chạy.
- **Bằng chứng / commit / thời điểm / người kiểm tra:** Chưa có.
- **Mã cũ (chỉ đối chiếu):** C5-T02.
- **Trạng thái:** NOT_RUN.

## Bàn giao A

Đủ test bắt buộc và regression theo domain mới đề nghị REVIEW; reviewer xác nhận VERIFIED theo TESTING_GUIDELINES. ALL1 còn cần AC01–AC12 trên Cloud Run. Mock UI/DB không chứng minh Gmail/Gemini/cloud thật.
