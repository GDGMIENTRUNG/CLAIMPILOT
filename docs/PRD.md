# PRD — ClaimPilot v3

## Giá trị sản phẩm

Nhân viên CSKH cần xử lý hồ sơ khiếu nại qua nhiều lượt trao đổi: đọc email, tra đơn, kiểm tra bằng chứng/chính sách, chọn phương án, phản hồi và theo dõi đến khi kết thúc. AI giảm thao tác lặp lại; người dùng kiểm soát quyết định và nội dung gửi.

## MVP hackathon 14/11/2026, 07:30–11:30

| Mục tiêu | Kết quả cần nghiệm thu |
|---|---|
| P1 Quyết định và audit | Nhiều vòng quyết định, phương án rõ, ghi chú và lịch sử |
| P2 Phản hồi | Xem/sửa → nhân viên bấm Gửi; Lưu Gmail Draft là lựa chọn phụ |
| P3 Năm nhóm policy | Xét vấn đề + yêu cầu, lý do/missing fields/next action/version |
| P4 Login + Cloud Run + sync | HTTPS, API bảo vệ, DB bền vững, lịch năm phút |
| P5 Dữ liệu kiểm thử | Fixtures lặp được, vòng bổ sung/ngoại lệ và kết quả Google thật để nghiệm thu sản phẩm |
| P6 Ảnh | Ảnh hai phía hoặc phân tích một phía có giới hạn, Gemini thật |

## Luồng và thành công

Gmail → hồ sơ có nhiều messages → AI/manual → xác minh/policy/ảnh → nhân viên chọn phương án → xem/sửa phản hồi → gửi hoặc nháp → chờ khách/thực hiện → resolved → đóng. Inbound mới mở lại để xem xét, không mất lịch sử. Chi tiết tại [WORKFLOW](WORKFLOW.md).

Thành công đo bằng [acceptance scenarios](ACCEPTANCE_MATRIX.md), không phần trăm code, độ chính xác AI hoặc lời hứa hoàn tất trong bốn giờ. Có Send trong app vẫn Human-in-the-Loop vì nhân viên kiểm tra nội dung cuối và chủ động xác nhận.

## Giới hạn

Một doanh nghiệp, một Gmail, một staff account, đơn mẫu. Không tự gửi theo AI/scheduler; không payment/refund API, video, tích hợp sàn/kho, multi-tenant hay split/merge phức tạp. Phương án đổi/hoàn được thực hiện bên ngoài và ghi nhận thủ công. Chính sách demo không đại diện chính sách thật của mọi doanh nghiệp.

## Trải nghiệm mong muốn

Nhân viên biết việc cần làm tiếp, lý do đánh giá, thông tin còn thiếu, tình trạng gửi và thực hiện. AI lỗi không khóa hồ sơ. Một account dùng chung không chứng minh danh tính riêng từng người; chưa quảng bá audit đa nhân viên.

## Phân công và release

Ba fullstack theo feature: A Workspace + nền Cloud Run, B Assessment/Evidence, C Resolution/Communication. Từng người làm UI/API/persistence/tests, dùng BASE contracts/harness để bắt đầu độc lập; một URL Cloud Run cho bản ghép. Không nhiệm vụ slide/thuyết trình/diễn tập; dữ liệu mẫu là fixture phục vụ build/test, không tính là một phần việc demo riêng. [SHARED_CONTRACTS](SHARED_CONTRACTS.md) và [release checklist](RELEASE_CHECKLIST.md).
