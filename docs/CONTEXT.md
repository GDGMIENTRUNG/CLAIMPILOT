# Context — CURRENT và TARGET AI-first v4

## CURRENT local cập nhật sau đợt docs
Đã chạy localhost8080: auth/session,5-tab workspace, KB/settings có persistence, manual assessment/decisions/composer/check/preview và provider adapters. CR-001 local đã migrate0006,20 bảng, backup/clone kiểm trước khi nâng, giữ dữ liệu cũ. UI desktop/mobile đã smoke với DB/API thật. Gửi Gmail mặc định tắt; cloud/Scheduler/GCS/reconcile/pilot chưa nghiệm thu. Các mục baseline/TARGET bên dưới mô tả lịch sử trước triển khai local; evidence mới trong IMPLEMENTATION_REPORT.

## Nguồn và thứ tự đọc
[AI_CUSTOMER_SUPPORT_REQUIREMENTS](AI_CUSTOMER_SUPPORT_REQUIREMENTS.md) là nguồn yêu cầu cho lần đồng bộ docs này. File nguồn giữ nguyên trạng thái đề xuất; tài liệu phụ chuyển thành thiết kế v4 để review. Đọc AGENTS → nguồn yêu cầu → context → WORKFLOW → TASK → SHARED_CONTRACTS → task cá nhân.

## CURRENT có bằng chứng lịch sử
Baseline đã merge main ở74d0936: React/Vite, FastAPI, PostgreSQL17; pipeline Gmail readonly và AI text cơ bản, dashboard list/filter/detail/sync/retry. ORM/schema0005 có13 bảng/203 cột. Đã thử migration mới/cũ/backfill/repeat/drift,92 backend tests và Docker Node22/Python3.11, browser desktop/mobile. Xem [IMPLEMENTATION_REPORT](../IMPLEMENTATION_REPORT.md); đây là lịch sử, không phải chạy lại hôm nay.

Chưa có auth/Principal/CaseStore/registry/harness/thread workflow đầy đủ. Chưa KB, settings doanh nghiệp, agent orchestration/safety/citations hoặc UI5 mục. Code cũ ghi projection legacy; có bảng không có nghĩa luồng nghiệp vụ đã chạy.

Cloud có scripts chuẩn bị; lần kiểm gần nhất project claimpilot-513010 chưa gắn billing, các billing accounts nhìn thấy đều đóng. Credit người dùng cung cấp kết thúc14/11/2026 không chứng minh billing đã active. Kiểm thực tế trước cloud; không hardcode trạng thái này thành điều kiện thành công. Local app/DB đã được tắt theo yêu cầu trước; đợt docs không mở lại.

## TARGET
Workspace AI-first: Tổng quan/Hộp thư/Knowledge Base/Dữ liệu & Tích hợp/Cài đặt. Pipeline intake → lookup → policy/KB và evidence → đề xuất → staff decision → reply writer → safety/quality → staff preview/confirmed send → manual fulfillment/close. Follow-up mở lại cùng thread, nguyên bản/history được giữ.

Một doanh nghiệp/Gmail/staff; không multi-tenant, omnichannel, payment, auto-send hay sao chép Chatwoot. AI roles khác developer A/B/C; không tự spawn coding agents.

## Khoảng thiếu storage và quyền đợt này
13 bảng đủ phạm vi v3, chưa đủ REQ-007/009/012–020 của v4. CR-001 trong DATABASE_DESIGN đề xuất7 bảng mới; tổng20 chỉ là TARGET nếu được duyệt. Không có migration0006 hoặc schema mới được tạo trong đợt này. Dùng existing mappings; phần cần extension giữ BLOCKED_CR cho tới review, không mock production hoặc thêm JSON keys ngoài contract.

## Làm việc
Giữ12 FS task IDs, mở rộng nội dung theo role: A shell/settings/platform, B KB/assessment/retrieval, C source-aware composer/safety/send. BASE còn thiếu interfaces; B/C dùng doubles trong test/dev.78 test cũ +18 test mới =96 test đặc tả; tất cả NOT_RUN, không suy từ92 automated tests lịch sử. Task/evidence/reviewer tại TASK và TESTING_GUIDELINES.
