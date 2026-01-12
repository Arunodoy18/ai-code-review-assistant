# Firebase / Google Cloud Deployment Guide

This guide explains how to run the AI Code Review Assistant on Google Cloud using Docker images, Cloud Run, MemoryStore (Redis), Cloud SQL (PostgreSQL), and Firebase Hosting. The goal is to keep production infrastructure close to the local defaults while preserving feature parity (GitHub integration, background workers, Redis caching, Celery tasks).

> **Prerequisites**
> - Google Cloud project with billing enabled
> - `gcloud` CLI v430+ and `firebase-tools` v13+
> - Docker (build and push images)
> - GitHub App credentials (App ID, webhook secret, private key)
> - OpenAI API key (or alternative LLM provider key)

---

## 1. Enable Required Google Cloud APIs

```bash
PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  secretmanager.googleapis.com
```

---

## 2. Provision Managed Services

### 2.1 Cloud SQL for PostgreSQL

```bash
REGION="us-central1"
INSTANCE_NAME="codereview-postgres"
DB_NAME="codereview_db"
DB_USER="codereview"
DB_PASSWORD="<secure-password>"

gcloud sql instances create $INSTANCE_NAME \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-3840 \
  --region=$REGION \
  --storage-type=SSD \
  --root-password=$DB_PASSWORD

gcloud sql databases create $DB_NAME --instance=$INSTANCE_NAME

gcloud sql users create $DB_USER --instance=$INSTANCE_NAME --password=$DB_PASSWORD
```

> **Networking:** For the simplest rollout, enable a public IP on the instance and add Cloud Run's egress ranges as authorized networks. For restricted networks, configure a VPC connector.

### 2.2 MemoryStore (Redis)

```bash
REDIS_INSTANCE="codereview-redis"

gcloud redis instances create $REDIS_INSTANCE \
  --region=$REGION \
  --size=1 \
  --tier=STANDARD_HA
```

Copy the displayed host and port; you'll transform them into a Redis URL (`redis://HOST:PORT/0`).

### 2.3 Secret Manager

Store sensitive values in Secret Manager:

```bash
secrets=(
  OPENAI_API_KEY
  GITHUB_APP_ID
  GITHUB_WEBHOOK_SECRET
  JWT_SECRET_KEY
  REDIS_URL
  DATABASE_URL
  GITHUB_APP_PRIVATE_KEY_B64
)

for secret in "${secrets[@]}"; do
  gcloud secrets create "$secret" --replication-policy=automatic
  # Add first version
  gcloud secrets versions add "$secret" --data-file=- <<'EOF'
  <secret-value-goes-here>
EOF
done
```

Recommended values:

- `DATABASE_URL=postgresql://codereview:<password>@<cloud-sql-host>:5432/codereview_db`
- `REDIS_URL=redis://<memorystore-host>:6379/0`
- `GITHUB_APP_PRIVATE_KEY_B64` = base64-encoded GitHub App private key PEM

Grant Cloud Run access later with `gcloud secrets add-iam-policy-binding`.

---

## 3. Build and Publish Docker Images

### 3.1 Create Artifact Registry Repositories

```bash
BACKEND_REPO="us-docker.pkg.dev/$PROJECT_ID/code-review/backend"
FRONTEND_REPO="us-docker.pkg.dev/$PROJECT_ID/code-review/frontend"

gcloud artifacts repositories create code-review \
  --repository-format=docker \
  --location=us \
  --description="AI Code Review images"
```

### 3.2 Build & Push Backend

```bash
docker build -t $BACKEND_REPO:latest backend

gcloud auth configure-docker us-docker.pkg.dev

docker push $BACKEND_REPO:latest
```

### 3.3 Build & Push Frontend (Static Bundle)

```bash
docker build -t $FRONTEND_REPO:build --target build frontend
# Export the built assets from the image
container_id=$(docker create $FRONTEND_REPO:build)
docker cp "$container_id":/app/dist ./dist
docker rm "$container_id"
```

The frontend is deployed with Firebase Hosting, so we only need the `dist/` artifacts.

---

## 4. Deploy Backend to Cloud Run

### 4.1 FastAPI Service

```bash
BACKEND_SERVICE="codereview-api"

gcloud run deploy $BACKEND_SERVICE \
  --image=$BACKEND_REPO:latest \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --min-instances=1 \
  --max-instances=3 \
  --set-env-vars "ENVIRONMENT=production" \
  --set-env-vars "ENABLE_GITHUB_INTEGRATION=true" \
  --set-env-vars "ENABLE_GITHUB_WEBHOOKS=true" \
  --set-env-vars "ENABLE_BACKGROUND_TASKS=true" \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest" \
  --set-secrets "GITHUB_APP_ID=GITHUB_APP_ID:latest" \
  --set-secrets "GITHUB_WEBHOOK_SECRET=GITHUB_WEBHOOK_SECRET:latest" \
  --set-secrets "JWT_SECRET_KEY=JWT_SECRET_KEY:latest" \
  --set-secrets "DATABASE_URL=DATABASE_URL:latest" \
  --set-secrets "REDIS_URL=REDIS_URL:latest" \
  --set-secrets "GITHUB_APP_PRIVATE_KEY_B64=GITHUB_APP_PRIVATE_KEY_B64:latest"
```

Cloud Run will inject the secrets as environment variables. The backend now resolves the GitHub private key by decoding `GITHUB_APP_PRIVATE_KEY_B64` into a temporary file.

### 4.2 Celery Worker Service

Deploy the same image with a different command:

```bash
WORKER_SERVICE="codereview-worker"

gcloud run deploy $WORKER_SERVICE \
  --image=$BACKEND_REPO:latest \
  --region=$REGION \
  --platform=managed \
  --max-instances=2 \
  --min-instances=0 \
  --set-env-vars "ENVIRONMENT=production" \
  --set-env-vars "ENABLE_GITHUB_INTEGRATION=true" \
  --set-env-vars "ENABLE_BACKGROUND_TASKS=true" \
  --set-secrets "OPENAI_API_KEY=OPENAI_API_KEY:latest" \
  --set-secrets "GITHUB_APP_ID=GITHUB_APP_ID:latest" \
  --set-secrets "GITHUB_WEBHOOK_SECRET=GITHUB_WEBHOOK_SECRET:latest" \
  --set-secrets "JWT_SECRET_KEY=JWT_SECRET_KEY:latest" \
  --set-secrets "DATABASE_URL=DATABASE_URL:latest" \
  --set-secrets "REDIS_URL=REDIS_URL:latest" \
  --set-secrets "GITHUB_APP_PRIVATE_KEY_B64=GITHUB_APP_PRIVATE_KEY_B64:latest" \
  --command "celery" \
  --args "-A" "app.tasks.celery_app" "worker" "--loglevel=info"
```

> **Important:** Disable HTTP ingress for the worker service (`--ingress internal`) because it only needs to consume Redis messages.

### 4.3 Authorize Secret Access

If deployment fails with secret permission errors, grant the Cloud Run service account access:

```bash
SERVICE_ACCOUNT="$(gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(spec.template.spec.serviceAccountName)')"
for secret in "${secrets[@]}"; do
  gcloud secrets add-iam-policy-binding "$secret" \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
done
```

Repeat for the worker service account if different.

---

## 5. Deploy Frontend with Firebase Hosting

### 5.1 Initialize Firebase Hosting

```bash
firebase login
firebase use $PROJECT_ID
firebase init hosting
# Select "dist" as the public directory when prompted
```

Copy the previously exported `dist/` folder into the repository root (or configure your CI pipeline to generate it). Update `firebase.json` rewrites so API calls route to Cloud Run:

```json
{
  "hosting": {
    "public": "dist",
    "rewrites": [
      {
        "source": "/api/**",
        "run": {
          "serviceId": "codereview-api",
          "region": "us-central1"
        }
      },
      { "source": "**", "destination": "/index.html" }
    ]
  }
}
```

Deploy:

```bash
firebase deploy --only hosting
```

---

## 6. GitHub App Configuration

1. In GitHub → Settings → Developer settings → GitHub Apps, edit or create your app.
2. Set **Webhook URL** to the Cloud Run URL for the backend `/api/webhooks/github` endpoint.
3. Use the same webhook secret stored in Secret Manager.
4. Generate a new private key, base64-encode it, and update the `GITHUB_APP_PRIVATE_KEY_B64` secret:
   ```bash
   base64 -w0 path/to/private-key.pem | gcloud secrets versions add GITHUB_APP_PRIVATE_KEY_B64 --data-file=-
   ```
5. Install the app on the repositories you want the assistant to monitor.

---

## 7. Observability & Maintenance

- **Logs:** `gcloud run logs read codereview-api --region=$REGION --follow`
- **Celery worker:** `gcloud run logs read codereview-worker --region=$REGION --follow`
- **Redis metrics:** Cloud Console → Memorystore → Instance → Monitoring
- **Database migrations:** Use `psql` via `gcloud sql connect` or run Alembic migrations within a temporary Cloud Run job.

Set up Cloud Scheduler to hit `/api/health/ready` or other keep-alive endpoints if you want to keep instances warm.

---

## 8. Cleanup

```bash
gcloud run services delete $BACKEND_SERVICE --region=$REGION
gcloud run services delete $WORKER_SERVICE --region=$REGION
gcloud sql instances delete $INSTANCE_NAME
gcloud redis instances delete $REDIS_INSTANCE --region=$REGION
firebase hosting:sites:delete $PROJECT_ID
```

---

## 9. Checklist for Production Readiness

- [ ] All secrets stored in Secret Manager and injected at runtime
- [ ] `ENABLE_GITHUB_INTEGRATION`, `ENABLE_GITHUB_WEBHOOKS`, and `ENABLE_BACKGROUND_TASKS` set to `true`
- [ ] Redis and PostgreSQL connection strings confirmed
- [ ] Celery worker service running and consuming tasks
- [ ] Firebase Hosting rewrites forwarding API traffic correctly
- [ ] GitHub App installed and webhook deliveries succeeding

With these steps complete, the AI Code Review Assistant runs in Google Cloud while matching the local development experience.
