# ClaimPilot

ClaimPilot là ứng dụng nội bộ đọc email khiếu nại từ Gmail, dùng AI để trích xuất thông tin, đối chiếu đơn hàng trong PostgreSQL và đề xuất kết quả để nhân viên xem xét.

> Ứng dụng không tự gửi email, hoàn tiền hoặc thực hiện giao dịch.

## Yêu cầu

- Python 3.11+
- Node.js 22+
- Docker và Docker Compose
- Google Cloud OAuth Client loại **Desktop app**
- Gemini API key

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
- `GEMINI_API_KEY` và model Gemini khả dụng với tài khoản.
- `AI_PROVIDER=gemini`.

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
5. Nếu AI lỗi, mở complaint và bấm **Retry Gemini analysis**.

Mỗi lần sync xử lý tối đa số thư trong `GMAIL_BATCH_SIZE`. `GMAIL_QUERY` lọc các ứng viên có dấu hiệu phàn nàn; AI tiếp tục xác định email có thực sự là complaint hay không rồi mới phân loại thành Late Delivery, Not Received, Damaged Item, Wrong Item, Refund Request hoặc Other. Thư quảng cáo và thư không liên quan được ghi nhận để tránh xử lý lặp lại nhưng không xuất hiện trên dashboard.

## Dữ liệu mẫu

| Đơn hàng | Email khách hàng | Trạng thái |
| --- | --- | --- |
| DH001 | hang290806@gmail.com | Đã giao trễ |
| DH002 | phannhungoc2k@gmail.com | Đã giao đúng hạn |
| DH003 | donchick24@gmail.com | Chưa xác nhận giao |

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
