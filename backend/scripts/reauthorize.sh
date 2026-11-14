#!/bin/bash
set -e
echo "1. Đang giải phóng cổng 8080..."
PIDS=$(lsof -ti :8080 2>/dev/null || true)
if [ -n "$PIDS" ]; then
    kill -9 $PIDS 2>/dev/null || true
    sleep 1
fi

echo "2. Mở trình duyệt để đăng nhập Google OAuth..."
cd "$(dirname "$0")/.."
.venv/bin/python scripts/authorize_gmail.py

echo "3. Đang khởi động lại máy chủ Web tại http://localhost:8080..."
nohup .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload --no-access-log > /dev/null 2>&1 &
sleep 2

echo "✅ Hoàn tất! Máy chủ đã hoạt động trở lại tại http://localhost:8080"
