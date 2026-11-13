# ClaimPilot

ClaimPilot là ứng dụng nội bộ đọc email khiếu nại từ Gmail, dùng AI để trích xuất thông tin, đối chiếu đơn hàng trong PostgreSQL và đề xuất kết quả để nhân viên xem xét.

> Ứng dụng không tự gửi email, hoàn tiền hoặc thực hiện giao dịch.

## Tài liệu SDD v3 — ba phần fullstack, Google Cloud Run

Kế hoạch build sản phẩm ngày 14/11/2026, 07:30–11:30: mỗi người tự UI/API/dữ liệu/tests theo luồng, không chia người backend/frontend/tích hợp và không task thuyết trình.

- [Bản đồ docs](docs/README.md), [hiện trạng](docs/CONTEXT.md), [luồng chuẩn](docs/WORKFLOW.md), [timeline](docs/IMPLEMENTATION_PLAN.md).
- [Task tổng](docs/TASK.md): [A Workspace + Cloud Run](docs/tasks/A_WORKSPACE.md), [B Assessment + Evidence](docs/tasks/B_ASSESSMENT.md), [C Resolution + Communication](docs/tasks/C_RESOLUTION.md).
- AI đọc [AGENTS](AGENTS.md), [BASE/ports/module owner](docs/SHARED_CONTRACTS.md), [API](docs/API_SPECIFICATION.md), [database](docs/DATABASE_DESIGN.md), [UI/UX](docs/UI_UX_SPECIFICATION.md), [prompt](docs/AI_PROMPTS.md).
- Test fullstack [A32](docs/test-cases/A_TEST_CASES.md), [B19](docs/test-cases/B_TEST_CASES.md), [C27](docs/test-cases/C_TEST_CASES.md); [AC01–AC12](docs/ACCEPTANCE_MATRIX.md), [release checklist](docs/RELEASE_CHECKLIST.md).

TARGET v3: Gmail → hồ sơ nhiều email → đánh giá/xác minh/ảnh → nhân viên quyết định → preview/edit → confirmed send hoặc draft → thực hiện ngoài app → close/reopen. Bắt buộc một URL Cloud Run cùng origin, Cloud SQL/Secrets/private Storage/Scheduler. Không auto-send theo AI/Scheduler hoặc tự refund.

BASE ngày 14/11 đã bổ sung models/schema 13 bảng/203 cột, migration `0005`, backfill và Docker một origin; database local đã nâng cấp, 92 backend tests đạt. FS tasks/harness/auth/Scheduler/send vẫn cần triển khai; 78 test nghiệm thu sản phẩm chưa được chạy. [Bằng chứng và giới hạn](IMPLEMENTATION_REPORT.md), [cấu hình Cloud Run chờ billing](docs/DEPLOYMENT.md).

## Chạy một URL bằng Docker

Giữ nguyên `.env` và `backend/.env` nếu đã cấu hình. Với máy mới, tạo hai file từ `.env.example` tương ứng trước. Backup DB có dữ liệu trước migration; không xóa volume.

```sh
docker-compose up -d db
docker-compose -f docker-compose.yml -f docker-compose.app.yml build app
docker-compose -f docker-compose.yml -f docker-compose.app.yml run --rm --no-deps app alembic upgrade head
docker-compose -f docker-compose.yml -f docker-compose.app.yml up -d app
```

Mở http://localhost:8080; API http://localhost:8080/api/health. Container dùng DB hiện có, bind loopback, không tự migrate hoặc seed khi startup. API key chưa có vẫn mở UI/health được; `.env` không được đóng vào image. Cấu hình local nạp key/provider hiện có từ `backend/.env`; token OAuth local vẫn được giữ ở máy, chưa mount vào container mặc định. Dùng luồng local mục 3 nếu cần đọc Gmail trước khi A/C hoàn tất tích hợp cloud.

Cloud Run: `bash infra/cloud-run.sh plan` xem cấu hình; `preflight` chỉ đọc trạng thái. Chưa deploy: project `claimpilot-513010` có billing chưa hoạt động. Cloud bootstrap giữ IAM private đến khi A làm đăng nhập.

## Yêu cầu

- Python 3.11+
- Node.js 22+
- Docker và Docker Compose
- Google Cloud OAuth Client loại **Desktop app**
- Gemini API key; có thể dùng Groq tạm thời trong quá trình phát triển

## 1. Cấu hình

Từ thư mục gốc:

```sh
cp .env.example .env
cp backend/.env.example backend/.env
```

Cập nhật:

- `POSTGRES_PASSWORD` trong `.env`.
- `DATABASE_URL` trong `backend/.env` với cùng mật khẩu.
- `GOOGLE_CLIENT_ID` và `GOOGLE_CLIENT_SECRET`.
- Với cấu hình chính: đặt `GEMINI_API_KEY`, model khả dụng và `AI_PROVIDER=gemini`.
- Nếu hạn mức Gemini chưa sẵn sàng: đặt `GROQ_API_KEY` và `AI_PROVIDER=groq` để kiểm thử tạm thời.

Không commit `.env`, API key hoặc `backend/.secrets/` lên Git.

## 2. Khởi tạo database và backend

```sh
docker-compose up -d db
python3 -m venv backend/.venv
backend/.venv/bin/pip install -r backend/requirements.txt

cd backend
.venv/bin/alembic upgrade head
.venv/bin/python -m scripts.seed_data
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Nếu máy dùng Docker Compose plugin, thay `docker-compose` bằng `docker compose`.

API docs: http://127.0.0.1:8000/docs

## 3. Cấp quyền đọc Gmail

Trong Google Cloud:

1. Bật Gmail API.
2. Cấu hình OAuth consent screen và thêm tài khoản test user.
3. Tạo OAuth Client loại **Desktop app**.
4. Dùng scope `https://www.googleapis.com/auth/gmail.readonly`.
5. Giữ callback mặc định `http://localhost:8080/`.

Chạy lệnh sau trong `backend/`:

```sh
.venv/bin/python -m scripts.authorize_gmail
```

Chọn tài khoản Gmail cần đọc. Token được lưu cục bộ tại `backend/.secrets/gmail-token.json`.

## 4. Chạy frontend

Mở terminal khác tại thư mục gốc:

```sh
npm --prefix frontend ci
npm --prefix frontend run dev
```

Mở http://localhost:5173.

## 5. Sử dụng

1. Gửi email khiếu nại vào Gmail đã cấp quyền.
2. Email nên chứa mã đơn như `DH001`, `DH002` hoặc `DH003`.
3. Mở dashboard và bấm **Sync Emails**.
4. Chọn complaint để xem email gốc, phân tích AI, đơn hàng xác minh và kết quả chính sách.
5. Nếu AI lỗi, mở complaint và bấm **Retry AI analysis**.

Mỗi lần sync xử lý tối đa số thư trong `GMAIL_BATCH_SIZE`. `GMAIL_QUERY` lọc các ứng viên có dấu hiệu phàn nàn; AI tiếp tục xác định email có thực sự là complaint hay không rồi mới phân loại thành Late Delivery, Not Received, Damaged Item, Wrong Item, Refund Request hoặc Other. Thư quảng cáo và thư không liên quan được ghi nhận để tránh xử lý lặp lại nhưng không xuất hiện trên dashboard.

## Dữ liệu mẫu

| Đơn hàng | Email khách hàng        | Trạng thái         |
| -------- | ----------------------- | ------------------ |
| DH001    | hang290806@gmail.com    | Đã giao trễ        |
| DH002    | phannhungoc2k@gmail.com | Đã giao đúng hạn   |
| DH003    | donchick24@gmail.com    | Chưa xác nhận giao |

Email người gửi phải trùng email khách hàng của đơn; nếu không, hệ thống yêu cầu nhân viên xác minh quyền sở hữu.

## Chính sách mẫu

- Giao trễ và yêu cầu hoàn phí vận chuyển: `eligible_for_review`.
- Giao đúng hạn: `not_eligible`.
- Chưa giao, thiếu dữ liệu hoặc yêu cầu ngoài chính sách: `insufficient_information`.
- Không tìm thấy mã đơn: `order_not_found`.

Mọi kết quả đều cần nhân viên xem xét. Hệ thống không tự hoàn tiền.

## Kiểm thử

```sh
cd backend
.venv/bin/pytest -q

cd ../frontend
npm run build
npm run test:e2e
```

Các dịch vụ Google được mock trong kiểm thử tự động. Kết nối Gmail/Gemini thật cần kiểm tra thủ công.

Gemini là provider AI chính theo thiết kế của ClaimPilot. Adapter Groq được giữ làm phương án tạm thời cho phát triển và kiểm thử khi hạn mức Gemini chưa sẵn sàng. Giao diện dùng nhãn trung lập **AI-powered analysis**; API trạng thái vẫn báo đúng provider và model đang chạy.

## Dừng ứng dụng

- Backend/frontend: nhấn `Ctrl+C` trong terminal tương ứng.
- PostgreSQL:

```sh
docker-compose stop db
```

Không xóa Docker volume nếu muốn giữ dữ liệu complaint.

## Xử lý lỗi thường gặp

- **Gmail authorization failed:** kiểm tra Desktop OAuth client, test user và callback `http://localhost:8080/`, sau đó cấp quyền lại.
- **Gemini unavailable/timeout:** kiểm tra API key, model, quota và mạng; sau đó dùng Retry hoặc Sync lại.
- **Sender mismatch:** gửi complaint từ đúng email khách hàng của đơn.
- **Không thấy email:** kiểm tra Inbox, thời gian trong `GMAIL_QUERY` và từ khóa complaint.
- **Frontend không kết nối backend:** xác nhận backend chạy tại `127.0.0.1:8000`.

ClaimPilot là MVP chạy cục bộ cho một nhân viên. Chưa có đăng nhập dashboard, gửi phản hồi, xử lý thanh toán, đồng bộ nền hoặc triển khai công khai.
