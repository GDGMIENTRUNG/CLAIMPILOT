FROM node:22-bookworm-slim AS frontend
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080 \
    FRONTEND_DIST=/app/frontend/dist GMAIL_TOKEN_READ_ONLY=true
WORKDIR /app/backend
COPY backend/requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt \
    && useradd --create-home --uid 10001 claimpilot
COPY backend/app ./app
COPY backend/migrations ./migrations
COPY backend/scripts ./scripts
COPY backend/alembic.ini ./
COPY --from=frontend /build/frontend/dist /app/frontend/dist
USER 10001
EXPOSE 8080
# Migrations run explicitly, once, in a separate command/Cloud Run Job.
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port \"${PORT:-8080}\" --workers 1"]
