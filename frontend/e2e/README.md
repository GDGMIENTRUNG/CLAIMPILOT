# Browser checks — workspace local

Từ thư mục `frontend`, chạy `npm run build` rồi `npm run test:e2e`. Cần PostgreSQL local, backend/.venv đã cài dependencies và Google Chrome trên máy. Playwright tự khởi động API thật tại127.0.0.1:8082, dùng schema `e2e_<UUID>` riêng và credential tổng hợp trong thư mục tạm, rồi dọn đúng schema/credential của lượt chạy. Không dùng bảng dữ liệu ứng dụng; toàn bộ AI/Gmail credentials và Gmail write bị tắt trong tiến trình test. Không cần dừng workspace8080.

`workspace.spec.ts` kiểm desktop1512px/mobile390px: đăng nhập → lưu cấu hình → tạo KB có hạn hiệu lực/rà soát → gửi duyệt/xuất bản → lịch sử → quyết định → soạn/lưu/preview → đọc trích dẫn → settings đổi vô hiệu preview → staff review-context → quyết định mới không mang nội dung chưa lưu của quyết định cũ. Test kiểm không tràn ngang/JS error, lưu screenshot vào `test-results/workspace-{desktop,mobile}.png`; trace giữ khi thất bại. Đây là browser/API/PostgreSQL thật với dữ liệu tổng hợp; không chứng minh AI/Gmail/cloud thật.

## Bộ dashboard baseline lịch sử

`dashboard.spec.ts`/`playwright.config.ts` thuộc giao diện baseline trước v4 và được tách qua `npm run test:e2e:legacy`; không dùng làm nghiệm thu UI hiện hành. Các hướng dẫn bên dưới chỉ áp dụng khi chủ động chạy lại frontend/API baseline lịch sử.

Start FastAPI on 127.0.0.1:8000 and Vite on localhost:5173. The real-backend test expects the initial empty complaint database and no Gmail token (the default development setup); it performs a sync request and checks the real missing-authorization response. Do not run that test against an authorized/live inbox.

```sh
cd frontend
npx playwright install chromium
npm run test:e2e
```

For an already connected workspace, run only fixture-based checks:

```sh
npm run test:e2e -- --grep 'fixture-based|backend errors'
```

The populated-detail and backend-error tests intercept API responses with explicit fixtures. They verify UI behavior and escaping only, not live Google integrations. Each test runs at desktop and mobile sizes. No test sends emails or executes refunds.
