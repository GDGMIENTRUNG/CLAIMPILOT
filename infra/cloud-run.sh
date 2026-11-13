#!/usr/bin/env bash
# Configuration only in the BASE delivery. Default is a non-mutating plan.
set -euo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG_FILE="${CLAIMPILOT_CLOUD_CONFIG:-$ROOT_DIR/infra/cloud-run.env}"
if [[ ! -f "$CONFIG_FILE" ]]; then CONFIG_FILE="$ROOT_DIR/infra/cloud-run.env.example"; fi
# This is a local, trusted shell config containing only non-secret settings.
source "$CONFIG_FILE"
PROJECT_ID="${PROJECT_ID:?}"
REGION="${REGION:?}"
SQL_CONNECTION="$PROJECT_ID:$REGION:$SQL_INSTANCE"
RUNTIME_SA="claimpilot-runtime@$PROJECT_ID.iam.gserviceaccount.com"
MIGRATOR_SA="claimpilot-migrator@$PROJECT_ID.iam.gserviceaccount.com"
ACTION="${1:-plan}"

preflight() {
  command -v gcloud >/dev/null
  gcloud projects describe "$PROJECT_ID" --format='value(projectId,lifecycleState)'
  if [[ "$(gcloud billing projects describe "$PROJECT_ID" --format='value(billingEnabled)')" != True ]]; then
    echo 'Billing chưa hoạt động: dừng ở cấu hình, chưa tạo/deploy tài nguyên.' >&2
    return 3
  fi
}

ensure_sa() {
  if ! gcloud iam service-accounts describe "$1@$PROJECT_ID.iam.gserviceaccount.com" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud iam service-accounts create "$1" --project="$PROJECT_ID"
  fi
}

ensure_secret() {
  if ! gcloud secrets describe "$1" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud secrets create "$1" --replication-policy=automatic --project="$PROJECT_ID"
  fi
  gcloud secrets add-iam-policy-binding "$1" --project="$PROJECT_ID" \
    --member="serviceAccount:$2" --role=roles/secretmanager.secretAccessor >/dev/null
}

if [[ "$ACTION" == plan ]]; then
  cat <<EOF
Project: $PROJECT_ID; region: $REGION
Một Cloud Run service private IAM: $SERVICE
SQL: $SQL_CONNECTION / $SQL_DATABASE (PostgreSQL17)
Bucket private: gs://$BUCKET
SA riêng: runtime, migrator, scheduler; DB URLs/secrets riêng.
Thứ tự: preflight → provision → cấp DB users/quyền + secrets → build → migrate → deploy.
Không tạo Scheduler job khi route OIDC/DB lock chưa được A hoàn thành.
Chưa bật public access: phiên bản hiện tại chưa có đăng nhập ứng dụng.
Đọc docs/DEPLOYMENT.md trước khi thực thi. plan không gọi Google Cloud.
EOF
  exit 0
fi
if [[ "$ACTION" == preflight ]]; then preflight; exit; fi
case "$ACTION" in provision|build|migrate|deploy) ;; *) echo 'Actions: plan|preflight|provision|build|migrate|deploy' >&2; exit 2 ;; esac
if [[ "${2:-}" != --apply ]]; then
  echo "Chỉ preview cấu hình: dùng '$0 $ACTION --apply' khi đã vào task triển khai Cloud Run." >&2
  exit 2
fi
preflight

if [[ "$ACTION" == provision ]]; then
  gcloud services enable run.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com \
    artifactregistry.googleapis.com cloudbuild.googleapis.com storage.googleapis.com \
    cloudscheduler.googleapis.com gmail.googleapis.com --project="$PROJECT_ID"
  for account in claimpilot-runtime claimpilot-migrator claimpilot-scheduler; do ensure_sa "$account"; done
  for account in "$RUNTIME_SA" "$MIGRATOR_SA"; do
    gcloud projects add-iam-policy-binding "$PROJECT_ID" --member="serviceAccount:$account" --role=roles/cloudsql.client >/dev/null
  done
  if ! gcloud artifacts repositories describe "$REPOSITORY" --location="$REGION" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud artifacts repositories create "$REPOSITORY" --repository-format=docker --location="$REGION" --project="$PROJECT_ID"
  fi
  if ! gcloud sql instances describe "$SQL_INSTANCE" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud sql instances create "$SQL_INSTANCE" --database-version=POSTGRES_17 --edition=ENTERPRISE \
      --tier=db-custom-1-3840 --region="$REGION" --availability-type=zonal \
      --storage-size=10GB --storage-type=SSD --backup-start-time=03:00 --deletion-protection --project="$PROJECT_ID"
  fi
  if ! gcloud sql databases describe "$SQL_DATABASE" --instance="$SQL_INSTANCE" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud sql databases create "$SQL_DATABASE" --instance="$SQL_INSTANCE" --project="$PROJECT_ID"
  fi
  if ! gcloud storage buckets describe "gs://$BUCKET" --project="$PROJECT_ID" >/dev/null 2>&1; then
    gcloud storage buckets create "gs://$BUCKET" --location="$REGION" --uniform-bucket-level-access --public-access-prevention --project="$PROJECT_ID"
  fi
  # Enforce privacy on a pre-existing bucket too; never grant allUsers.
  gcloud storage buckets update "gs://$BUCKET" --uniform-bucket-level-access --public-access-prevention --project="$PROJECT_ID"
  gcloud storage buckets add-iam-policy-binding "gs://$BUCKET" --member="serviceAccount:$RUNTIME_SA" --role=roles/storage.objectUser --project="$PROJECT_ID" >/dev/null
  ensure_secret claimpilot-db-runtime "$RUNTIME_SA"
  ensure_secret claimpilot-db-migrator "$MIGRATOR_SA"
  for secret in claimpilot-gemini-key claimpilot-groq-key claimpilot-gmail-token; do ensure_secret "$secret" "$RUNTIME_SA"; done
  echo 'Tài nguyên nền xong; chưa có DB users, secret versions, migration, deployment hay Scheduler job.'
  exit 0
fi

: "${IMAGE_TAG:?Điền IMAGE_TAG duy nhất vào infra/cloud-run.env}"
IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$SERVICE:$IMAGE_TAG"
if [[ "$ACTION" == build ]]; then
  # Cloud Build's Linux builder produces the amd64 image needed by Cloud Run.
  gcloud builds submit "$ROOT_DIR" --tag="$IMAGE" --project="$PROJECT_ID" --ignore-file="$ROOT_DIR/.gcloudignore"
  exit 0
fi

if [[ "$ACTION" == migrate ]]; then
  gcloud run jobs deploy "$SERVICE-migrate" --image="$IMAGE" --region="$REGION" --project="$PROJECT_ID" \
    --service-account="$MIGRATOR_SA" --set-cloudsql-instances="$SQL_CONNECTION" \
    --set-secrets="DATABASE_URL=claimpilot-db-migrator:$DB_MIGRATOR_SECRET_VERSION" \
    --command=alembic --args=upgrade,head --tasks=1 --parallelism=1 --max-retries=0 --task-timeout=300s
  gcloud run jobs execute "$SERVICE-migrate" --wait --region="$REGION" --project="$PROJECT_ID"
  echo 'Cấp quyền DML bằng infra/runtime-grants.sql trước deploy; không dùng DB owner cho app.'
  exit 0
fi

SECRETS="DATABASE_URL=claimpilot-db-runtime:$DB_RUNTIME_SECRET_VERSION"
if [[ -n "${GEMINI_SECRET_VERSION:-}" ]]; then SECRETS+=",GEMINI_API_KEY=claimpilot-gemini-key:$GEMINI_SECRET_VERSION"; fi
if [[ -n "${GROQ_SECRET_VERSION:-}" ]]; then SECRETS+=",GROQ_API_KEY=claimpilot-groq-key:$GROQ_SECRET_VERSION"; fi
if [[ -n "${GMAIL_SECRET_VERSION:-}" ]]; then SECRETS+=",/secrets/gmail/token.json=claimpilot-gmail-token:$GMAIL_SECRET_VERSION"; fi
gcloud run deploy "$SERVICE" --image="$IMAGE" --region="$REGION" --project="$PROJECT_ID" \
  --service-account="$RUNTIME_SA" --set-cloudsql-instances="$SQL_CONNECTION" \
  --set-secrets="$SECRETS" --set-env-vars="AI_PROVIDER=$AI_PROVIDER,GEMINI_MODEL=$GEMINI_MODEL,GROQ_MODEL=$GROQ_MODEL,GCS_BUCKET=$BUCKET,GMAIL_TOKEN_PATH=/secrets/gmail/token.json,GMAIL_TOKEN_READ_ONLY=true" \
  --port=8080 --cpu=1 --memory=1Gi --timeout=300 --concurrency=8 --max-instances=1 --min-instances=0 \
  --no-allow-unauthenticated
BASE_URL="$(gcloud run services describe "$SERVICE" --region="$REGION" --project="$PROJECT_ID" --format='value(status.url)')"
gcloud run services update "$SERVICE" --region="$REGION" --project="$PROJECT_ID" --update-env-vars="FRONTEND_ORIGIN=$BASE_URL"
echo "Service private: $BASE_URL. Dùng gcloud run services proxy để mở UI local có IAM."
