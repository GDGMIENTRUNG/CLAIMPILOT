# ClaimPilot — Tổng quan AI-first Customer Support

## Nội dung và vấn đề
ClaimPilot là workspace AI hỗ trợ doanh nghiệp xử lý khiếu nại qua Gmail từ tiếp nhận đến phản hồi/đóng hồ sơ. Nhân viên hiện phải tự đọc email, nối thread, tìm đơn, kiểm policy/ảnh và viết câu trả lời. Dữ liệu rời rạc, tri thức thiếu duyệt/version và kết quả AI thiếu nguồn khiến xử lý chậm, không nhất quán, khó kiểm chứng.

Sản phẩm tự điều phối phân tích và chuẩn bị phản hồi. Nhân viên tập trung vào thiếu dữ liệu/bất đồng/ngoại lệ, duyệt quyết định và xác nhận nội dung cuối. AI không tự gửi, hoàn tiền, thực hiện fulfillment hay đóng hồ sơ.

## Workspace và chức năng
| Mục | Chức năng |
|---|---|
| Tổng quan | Work queues, agent progress, lỗi và last sync |
| Hộp thư | Search/filter, nhiều email/thread, conversation/history/context, decision và composer |
| Knowledge Base | Soạn/sửa/tìm bài, submit/approve/publish/archive, version/hiệu lực và citation |
| Dữ liệu & Tích hợp | Gmail status/deferred, orders/policy/nguồn và thông tin thiếu |
| Cài đặt | Doanh nghiệp/ngôn ngữ/giọng điệu, optional roles và ngưỡng review; guardrails bắt buộc |

## Luồng
Gmail → intake/classification → lookup đơn → policy + nguồn KB đã duyệt và evidence → hiển thị kết quả/ngoại lệ → nhân viên quyết định → reply writer → safety/quality → nhân viên sửa/lưu/preview/xác nhận gửi → Gmail → chờ khách/thực hiện ngoài app → resolved/closed. Follow-up cập nhật cùng hồ sơ, mở lại khi cần và làm nội dung cũ cần review.

Agent là6 năng lực phần mềm có tiến độ/nguồn/version; không phải6 nhân viên hoặc6 microservices. Gmail timeout sau dispatch là unknown, cần reconcile, không auto resend. KB nháp/hết hiệu lực/mâu thuẫn không thành nguồn đáng tin. Chỉnh cấu hình không sửa ngược thư cũ.

## Ba developer
A fullstack workspace/auth/intake/search/settings/orchestration/platform. B fullstack lookup/policy/KB/retrieval/evidence và source/version safety. C fullstack decision/composer/reply citations/quality/send/fulfillment. Cả ba tự UI/API/persistence/tests; cùng một image React/FastAPI, Cloud SQL, private GCS, Secrets và Scheduler.

## Đã có và còn thiếu
CURRENT: ứng dụng Gmail/AI/dashboard ban đầu;13 bảng/203 cột/migration0005; Docker cùng origin;92 tests và desktop/mobile smoke lịch sử; code baseline đã lên main74d0936. Chưa có đầy đủ auth/CaseStore/agent runtime/KB/settings/workflow mới hoặc cloud live.
Schema13 bảng chỉ đủ v3. CR-001 đề xuất7 bảng bổ sung, cần review trước migration. Yêu cầu mới và96 test đặc tả vẫn chưa là tính năng hoàn thành; cloud cần kiểm billing/IAM/OAuth/quota thực tế.

## Thành công và giới hạn
SC-001–007 là mục tiêu pilot về đúng thread, tiến độ, nguồn, human confirmation, usability và tiết kiệm thời gian; cần dataset/rubric/manual baseline trước tuyên bố đạt. Một doanh nghiệp, một Gmail, một staff; không omnichannel/multi-tenant/payment/auto-send. Chatwoot chỉ là tham khảo tổ chức workspace.

Nguồn: [requirements](docs/AI_CUSTOMER_SUPPORT_REQUIREMENTS.md), [task](docs/TASK.md), [database](docs/DATABASE_DESIGN.md), [API](docs/API_SPECIFICATION.md), [UI](docs/UI_UX_SPECIFICATION.md), [evidence lịch sử](IMPLEMENTATION_REPORT.md).
