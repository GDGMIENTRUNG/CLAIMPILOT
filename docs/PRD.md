# PRD — ClaimPilot AI-first v4

Nguồn yêu cầu: [AI_CUSTOMER_SUPPORT_REQUIREMENTS](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md), REQ-001–032. Đây là bản diễn giải để review/triển khai; cập nhật docs không có nghĩa tính năng hoặc thay đổi schema đã được duyệt triển khai.

## Vấn đề và giá trị
Nhân viên đang tự đọc email, nối hội thoại, tìm đơn, tra chính sách, kiểm ảnh và viết lại cùng loại phản hồi. Thiếu tri thức đã duyệt, nguồn căn cứ và tiến độ xử lý khiến đề xuất AI khó kiểm chứng. ClaimPilot điều phối các vai trò phần mềm để tự chuẩn bị hồ sơ, nguồn và nội dung; nhân viên xử lý ngoại lệ, quyết định phương án và xác nhận gửi.

## Người dùng và phạm vi
Một doanh nghiệp, một Gmail, một staff account, hồ sơ liên quan đơn hàng. AI agent là năng lực phần mềm, không phải developer A/B/C hoặc tài khoản nhân viên. Giữ React/FastAPI/PostgreSQL và một URL Cloud Run. Không omnichannel, multi-tenant, payment, tự gửi, tự fulfillment hoặc tự đóng.

## Trải nghiệm đích
Năm mục điều hướng: Tổng quan, Hộp thư, Knowledge Base, Dữ liệu & Tích hợp, Cài đặt. Inbox desktop ba vùng danh sách/hội thoại/ngữ cảnh; mobile một cột với Hội thoại/Đánh giá/Lịch sử. Kết quả agent hiển thị vai trò, trạng thái, nguồn, thời điểm, dữ liệu thiếu và bước tiếp theo; AI và nghiệp vụ có trạng thái độc lập.

## Phạm vi ưu tiên
| Ưu tiên | Khả năng | Yêu cầu |
|---|---|---|
| P1 | Hội thoại/thread/search, tiến độ agent và ngoại lệ | REQ-001–011 |
| P1 | KB có duyệt, version, hiệu lực, citation và xử lý mâu thuẫn | REQ-012–015 |
| P1 | Quyết định người thật, preview/send, chống gửi trùng, audit và fallback manual | REQ-021–027 |
| P1 | Same origin, auth/privacy, keyboard/mobile, lỗi giữ input | REQ-028–032 |
| P2 | Xem dữ liệu/tích hợp, chỉnh doanh nghiệp và cấu hình agent | REQ-016–020 |

P2 vẫn là yêu cầu đích; bản chỉ hoàn thành P1 phải ghi rõ phạm vi, không báo toàn bộ v4 hoàn thành. Năm policy và phân tích ảnh hiện hành tiếp tục có hiệu lực.

## Thành công và bằng chứng
SC-001–007 là mục tiêu pilot đề xuất, không kết quả: đúng thread ≥95%; trạng thái/bước tiếp theo ≥90%; xác nhận gửi 100%; có căn cứ hoặc đánh dấu cần review ≥95%; thao tác trong workspace ≥90%; thời gian trung vị giảm ≥30%; ngoại lệ hiển thị 100%. Phải ghi dataset, mẫu số, rubric, baseline manual và giới hạn đo; chưa pilot thì NOT_RUN.

## Hiện trạng và phân công
Baseline0005 có13 bảng/203 cột và92 tests lịch sử. Chưa có KB/settings/agent orchestration v4. [CR-001](DATABASE_DESIGN.md#cr-001--mở-rộng-ai-first-v4-đề-xuất) mô tả phần lưu trữ thiếu, chưa cho phép migrate.
A: workspace/settings/integrations/platform; B: assessment/KB/retrieval/agent steps; C: composer/safety/citations/send/lifecycle. Mỗi người fullstack; giữ12 mã FS, xem [TASK](TASK.md).
