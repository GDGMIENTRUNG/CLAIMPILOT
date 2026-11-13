# Testing guidelines — fullstack v3

## Bộ test theo phần sản phẩm

- [A Workspace + Cloud Run: 32 cases](test-cases/A_TEST_CASES.md), FS-A1..FS-A4.
- [B Assessment + Evidence: 19 cases](test-cases/B_TEST_CASES.md), FS-B1..FS-B4.
- [C Resolution + Communication: 27 cases](test-cases/C_TEST_CASES.md), FS-C1..FS-C4.

78 cases được phân bổ lại từ bộ trước, không tính số test là số tính năng hoàn thành. Mỗi test có dòng “Mã cũ” để đối chiếu ID cũ/mới; báo cáo mới dùng FS-ID. Toàn bộ cases vẫn NOT_RUN, task vẫn TODO. MERGE trước ghép, RELEASE trước nghiệm thu sản phẩm, không mốc diễn tập trình bày.

Mỗi fullstack tự viết/chạy UI/API/DB tests phần mình. [BASE harness và ports](SHARED_CONTRACTS.md) cho phép dùng test doubles đúng contract khi domain khác chưa có runtime; không phải quyền chạy mocks trên Cloud Run release. Variants trong case cần kết quả từng biến thể, không PASS cả nhóm từ một happy path.

Database khóa là CLAIMPILOT_MVP_DB_V1 trong [DATABASE_DESIGN](DATABASE_DESIGN.md):13 bảng/203 cột, DB01–DB12 hiện NOT_RUN. Bổ sung biến thể FK cùng case/reply, failed/stale runs, intake failures và closure metadata vào test hiện có, tổng vẫn78cases. BASE chỉ VERIFIED sau migration/backfill/constraint tests trên PostgreSQL, không từ việc file đặc tả đã chốt.

## Fixture chung và cách chạy tiết kiệm thời gian

Mỗi test có DB/schema hoặc fixtures riêng; thời gian cố định D0=2026-11-14, occurred_at mặc định 03:00:00Z (10:00 Việt Nam). Ngày bên dưới tính theo D0, không theo clock máy chạy test. Email dùng DEMO_CUSTOMER_EMAIL/GMAIL_ACCOUNT_EMAIL nhóm kiểm soát qua env; không ghi địa chỉ/credentials thật vào tài liệu.

| Fixture | Dữ liệu chuẩn ban đầu |
|---|---|
| F-LATE / CPDEMO001 | purchased D0-7, expected D0-4, actual D0-2, delivered; shipping_fee 40000; type late_delivery/action shipping_fee_refund; email matched |
| F-NOT-RECEIVED / CPDEMO002 | purchased D0-7, expected D0-3, actual null, in transit; type not_received/action request_information; email matched |
| F-DAMAGED / CPDEMO003 | delivered D0-2, type damaged_item/action replacement; ảnh khách thiếu ban đầu để test bổ sung, ảnh đơn giả sẵn khi test ảnh |
| F-WRONG / CPDEMO004 | delivered D0-1, type wrong_item/action replacement; có ảnh giả hai phía |
| F-REFUND / CPDEMO005 | delivered D0-3, type refund_request/action order_refund; total_amount giả lập 400000 hoặc null cho biến thể thiếu tiền |
| Boundary | Clone fixture rồi thay received/actual/expected để chạm grace1/2, return7/8; ngày purchased<=actual và ảnh hợp lệ trừ khi chính test đang kiểm dữ liệu sai |
| Missing/mismatch/unknown | Clone fixture, bỏ order ID hoặc dùng CPDEMO999 không tồn tại hoặc sender khác; không biến đổi fixture dùng chung giữa các tests |

Các giá trị này là dữ liệu test, không yêu cầu sửa đơn seed hiện có ngoài phạm vi fixtures đã giao trong BASE/FS tasks. Fixture snapshot phải ghi case_version/reply revision thực tế được tạo, không hardcode version sau nhiều mutations. Request-info/approved/sent/closed preconditions tạo bằng factory/helper đúng constraints hoặc gọi workflow; không giả sent trong live release.

Tự động hóa unit/DB/parameterized/browser cho nhóm MERGE; nhóm RELEASE dùng vài full-loop thật để thu nhiều quan sát. Có thể dùng lại cùng evidence cho nhiều test khi cùng revision/data và bằng chứng thể hiện đủ từng kỳ vọng; mỗi test vẫn phải liên kết đúng observation. Không cần gửi thêm thư thật chỉ để tăng số case. Fault injection chỉ mocks/DB thử.

## Mốc kiểm tra và completion gate

- MERGE: kiểm tra phần task trước khi ghép; dependency chưa chạy thật có thể mock đúng contract nếu test cho phép, phải ghi loại bằng chứng.
- RELEASE: bắt buộc trên bản tích hợp trước nghiệm thu. Không được bỏ vì thiếu thời gian rồi vẫn đánh dấu task VERIFIED.
- NOT_RUN: chưa thực hiện; PASS: đã chạy và mọi kỳ vọng/biến thể đạt; FAIL: đã chạy nhưng lệch kỳ vọng; BLOCKED: không đủ điều kiện chạy hoặc đánh giá (ghi nguyên nhân/owner gỡ). Không có SKIP được tính là PASS.
- Một task chỉ VERIFIED khi đủ test bắt buộc cho task, regression liên quan đạt, contract/outputs bàn giao đủ và có người khác review bằng chứng. Owner đề nghị REVIEW, reviewer xác nhận VERIFIED trong TASK. Reviewer có thể là người nhóm hoặc phiên AI khác được giao; không mặc định tin báo cáo tự viết.
- Một vai trò xong phần riêng không chứng minh toàn dự án xong. ALL1 cần AC01–AC12 trên revision cuối với đúng mock/DB/browser/live/cloud đã yêu cầu. Khi thay code sau kiểm tra, đánh giá lại tests liên quan trên revision mới, không dùng kết quả cũ vô điều kiện.

## Mẫu bằng chứng mỗi test

```text
Test ID / biến thể:
Task / FR / AC:
Time Asia/Ho_Chi_Minh:
Commit / branch / Cloud Run revision (nếu có):
Môi trường / fixture / case ID giả:
Command hoặc thao tác thực sự đã chạy:
Loại bằng chứng: static / unit / DB / browser-fixture / browser-real / Google-live / cloud
Kết quả thực tế so với từng kỳ vọng:
File log/report/screenshot sanitized hoặc assertion/call count:
PASS / FAIL / BLOCKED; nguyên nhân nếu chưa đạt:
Owner thực hiện / người review:
```

Điền vào case tương ứng hoặc liên kết report bàn giao; bảng TASK tóm tắt và trỏ tới report, không nhét secrets vào Git. Lệnh dự định chạy hoặc ảnh màn hình đẹp không đủ để ghi PASS. Kiểm tra test docs không phải thực thi chức năng mới.

## Baseline lịch sử, không phải chạy lại hôm nay

Khảo sát 13/11/2026: frontend build đạt; backend 31 passed/31 setup errors vì DB không kết nối. Chưa full suite pass, chưa Playwright/live Google/cloud trong lần khảo sát. Đợt docs-only không cần chạy lại ứng dụng; kiểm tra links, contracts và bảo toàn code.

## Khi triển khai tính năng

Từ root, kiểm tra Docker rồi:
```sh
docker compose up -d db
cd backend
.venv/bin/alembic current
.venv/bin/alembic heads
.venv/bin/alembic upgrade head
.venv/bin/alembic check
.venv/bin/pytest -q --tb=short
```
Dùng docker-compose nếu máy không có Compose plugin. DB tests hiện tạo/drop schema UUID riêng, không truncate app. TEST_DATABASE_URL có thể dùng DB riêng; không in connection string chứa password. Kiểm tra migration/backfill trên DB thử có fixture dữ liệu cũ trước cloud.

Từ root:
```sh
npm --prefix frontend run build
npm --prefix frontend run test:e2e
```
Playwright hiện cần backend/Vite 8000/5173 chạy riêng và browser binary; config chưa tự start server. Cập nhật auth fixtures đúng flow, không disable auth để suite xanh. Unit/DB tests mock Google; browser fixtures không phải live Google.

## Theo owner fullstack

| A | B | C |
|---|---|---|
| auth/workspace/conversation/Gmail read, core CaseStore/backfill, Cloud Run/SQL/Secrets/Scheduler/locks | manual/ownership/text/policy/assessment UI + DB, images/GCS/Gemini, snapshots/late AI | decisions/composer UI + DB, Gmail write/reserve-complete/unknown, fulfillment/close/reopen |

## Bắt buộc kiểm tra cạnh tranh

- Hai decision cùng version chỉ một thành công; audit tương ứng không bị tách transaction.
- Email mới append trong lúc AI hoặc send chạy không bị kết quả cũ ghi đè.
- Gửi cùng key/payload không gọi Google lần hai; key reuse sai payload 409.
- Gửi timeout + refresh/double click không tự resend; worker chết → unknown recovery.
- Reply body thay sau preview/revision mismatch không gửi nội dung chưa xác nhận.
- Remote Gmail draft edit/delete/send làm conflict/unknown đúng, không overwrite mù.
- New thread trùng order không gộp, known thread reply không keyword vẫn nhập, outbound không tạo case mới.

## Hồi quy giữ lại

Parsing MIME Unicode/HTML, Gmail pagination, dedupe, failed retry, non-complaint/candidate tri-state, AI schema/error sanitization, stats/list/detail và bàn phím/mobile. Khi projection cũ thay đổi có chủ đích, cập nhật assertion kèm hợp đồng, không xóa tests để né.

## Acceptance và bằng chứng

[ACCEPTANCE_MATRIX](ACCEPTANCE_MATRIX.md) định nghĩa AC01–AC12. Ghi thời điểm, commit/revision, case giả, provider/model, command, PASS/FAIL/BLOCKED và loại mock/DB/browser/live/cloud. Live send chỉ hộp thư nhóm kiểm soát, sau user click; screenshot không credentials. Chạy regression trên revision cuối sau ghép, không dùng số pass báo cáo cũ.

## Kiểm thử độc lập và điểm ghép

A contract tests CaseStore/Principal/GoogleClientFactory/metadata registry; B/C tự test routers/models/components với harness. B test late AI/manual protection, C test reserve-send-completion. Khi ghép chạy lại CaseStore integration bằng PostgreSQL thật và full-loop AC01–AC12; mọi development doubles phải thay real adapters, production startup cấm auth bypass/fake data.

Fixtures chuẩn bị theo domain (A orders/messages; B policy/evidence; C decisions/replies), không nhiệm vụ làm slide/diễn tập. Precondition sent chỉ factory trong isolated tests; live release cần actual controlled send. [RELEASE_CHECKLIST](RELEASE_CHECKLIST.md) thay tài liệu trình diễn. Cùng một live evidence được reuse khi revision/data đúng và chứng minh từng assertion, không tạo mail thử dư.
