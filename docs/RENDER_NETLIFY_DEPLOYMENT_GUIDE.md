# Render + Netlify Deployment Guide

Deploy the AI Code Review Assistant using Render (backend + databases) and Netlify (frontend). This is the simplest production deployment path with managed services and GitHub integration.

## Why Render + Netlify?

- **Render**: Managed PostgreSQL, Redis, automatic Docker deployments from GitHub
- **Netlify**: CDN-backed static hosting with instant rollbacks
- **Cost**: ~$25-40/month (cheaper than Firebase/Cloud Run)
- **Setup time**: ~20 minutes vs 60+ for GCP

---

## Prerequisites

- [ ] GitHub account with this repository
- [ ] Render account (free): https://render.com
- [ ] Netlify account (free): https://netlify.com
- [ ] OpenAI API key
- [ ] GitHub App credentials (App ID, webhook secret, private key)

---

## Phase 1: Render Backend Setup (15 mins)

### 1.1 Create PostgreSQL Database

1. Go to Render Dashboard → **New** → **PostgreSQL**
2. Settings:
   - **Name**: `codereview-db`
   - **Database**: `codereview_db`
   - **User**: `codereview`
   - **Region**: Oregon (us-west) or closest to you
   - **Plan**: Starter ($7/month) or Free (limited)
3. Click **Create Database**
4. **Save the Internal Database URL** (starts with `postgresql://...`)

### 1.2 Create Redis Instance

1. Render Dashboard → **New** → **Redis**
2. Settings:
   - **Name**: `codereview-redis`
   - **Region**: Same as database
   - **Plan**: Starter ($10/month) or Free
3. Click **Create Redis**
4. **Save the Internal Redis URL** (starts with `redis://...`)

### 1.3 Deploy Backend API (Web Service)

1. Render Dashboard → **New** → **Web Service**
2. Connect your GitHub repository
3. Settings:
   - **Name**: `codereview-api`
   - **Region**: Same as database/Redis
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Plan**: Starter ($7/month) or Free
   - **Dockerfile Path**: `Dockerfile`

4. **Environment Variables** (click "Add Environment Variable"):
   ```
   ENVIRONMENT=production
   DATABASE_URL=<from step 1.1>
   REDIS_URL=<from step 1.2>
   ENABLE_GITHUB_INTEGRATION=true
   ENABLE_GITHUB_WEBHOOKS=true
   ENABLE_BACKGROUND_TASKS=true
   OPENAI_API_KEY=<your-openai-key>
   GITHUB_APP_ID=<your-github-app-id>
   GITHUB_WEBHOOK_SECRET=<your-webhook-secret>
   JWT_SECRET_KEY=<generate with: openssl rand -hex 32>
   FRONTEND_URL=https://<your-netlify-app>.netlify.app
   PORT=10000
   ```

5. **GitHub App Private Key** (base64 encoded):
   ```bash
   # On your machine:
   base64 -w0 github-app-private-key.pem
   # Copy output and add as:
   GITHUB_APP_PRIVATE_KEY_B64=<base64-encoded-key>
   ```

6. Click **Create Web Service**

7. **Wait for first deploy** (~5 mins). Note the service URL: `https://codereview-api.onrender.com`

### 1.4 Deploy Celery Worker (Background Worker)

1. Render Dashboard → **New** → **Background Worker**
2. Connect same GitHub repository
3. Settings:
   - **Name**: `codereview-worker`
   - **Region**: Same as others
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Docker
   - **Plan**: Starter ($7/month)
   - **Start Command**: `celery -A app.tasks.celery_app worker --loglevel=info`

4. **Environment Variables** (same as API, except remove PORT and FRONTEND_URL):
   ```
   ENVIRONMENT=production
   DATABASE_URL=<from step 1.1>
   REDIS_URL=<from step 1.2>
   ENABLE_GITHUB_INTEGRATION=true
   ENABLE_BACKGROUND_TASKS=true
   OPENAI_API_KEY=<your-openai-key>
   GITHUB_APP_ID=<your-github-app-id>
   GITHUB_WEBHOOK_SECRET=<your-webhook-secret>
   JWT_SECRET_KEY=<same as API>
   GITHUB_APP_PRIVATE_KEY_B64=<same as API>
   ```

5. Click **Create Background Worker**

### 1.5 Initialize Database

1. Go to your backend service → **Shell** tab
2. Run:
   ```bash
   python init_db.py
   ```
3. Verify output shows tables created: `projects`, `analysis_runs`, `findings`

---

## Phase 2: Netlify Frontend Setup (5 mins)

### 2.1 Build Settings

1. Netlify Dashboard → **Add new site** → **Import an existing project**
2. Connect your GitHub repository
3. Settings:
   - **Branch**: `main`
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`

4. **Environment Variables**:
   ```
   VITE_API_URL=https://codereview-api.onrender.com
   ```

5. Click **Deploy site**

6. **Custom domain** (optional):
   - Site settings → Domain management → Add custom domain
   - Or use the auto-generated: `<random-name>.netlify.app`

### 2.2 Configure API Proxy (CORS Alternative)

1. Create `frontend/netlify.toml`:
   ```toml
   [[redirects]]
     from = "/api/*"
     to = "https://codereview-api.onrender.com/api/:splat"
     status = 200
     force = true
     headers = {X-From = "Netlify"}
   
   [[headers]]
     for = "/*"
     [headers.values]
       X-Frame-Options = "DENY"
       X-Content-Type-Options = "nosniff"
       Referrer-Policy = "strict-origin-when-cross-origin"
   ```

2. Commit and push:
   ```bash
   git add frontend/netlify.toml
   git commit -m "Add Netlify proxy config"
   git push origin main
   ```

3. Netlify will auto-deploy the update

---

## Phase 3: GitHub App Configuration (5 mins)

1. Go to GitHub → Settings → Developer settings → GitHub Apps → Your App
2. Update **Webhook URL**: `https://codereview-api.onrender.com/api/webhooks/github`
3. Verify **Webhook secret** matches your `GITHUB_WEBHOOK_SECRET`
4. **Permissions** (if not set):
   - Repository permissions:
     - Pull requests: Read & write
     - Contents: Read-only
     - Metadata: Read-only
   - Subscribe to events:
     - Pull request
     - Pull request review
5. Install the app on your target repositories

---

## Phase 4: Verification (5 mins)

### 4.1 Backend Health Check

```bash
curl https://codereview-api.onrender.com/api/health
# Should return: {"status":"healthy",...}

curl https://codereview-api.onrender.com/docs
# Should show Swagger UI
```

### 4.2 Worker Logs

1. Render Dashboard → `codereview-worker` → **Logs**
2. Verify you see: `celery@... ready` and `Connected to redis://...`

### 4.3 Frontend

1. Visit your Netlify URL: `https://<your-app>.netlify.app`
2. Dashboard should load
3. Check browser console for API connection

### 4.4 End-to-End Test

1. Open a pull request in a repo with the GitHub App installed
2. Check Render logs for webhook receipt
3. Verify analysis appears in dashboard
4. Check GitHub PR for AI review comment

---

## Auto-Deploy Setup

Both Render and Netlify auto-deploy on git push to `main`:

1. **Render**: Services → Settings → Auto-Deploy = Yes (enabled by default)
2. **Netlify**: Site settings → Build & deploy → Continuous deployment = Enabled

Push to main triggers:
- Netlify rebuild (frontend) ~2 mins
- Render rebuild (backend + worker) ~5 mins

---

## Cost Breakdown (Monthly)

| Service | Plan | Cost |
|---------|------|------|
| Render PostgreSQL | Starter | $7 |
| Render Redis | Starter | $10 |
| Render Web Service (API) | Starter | $7 |
| Render Background Worker | Starter | $7 |
| Netlify Hosting | Free | $0 |
| **Total** | | **$31/month** |

**Free tier option** (limited):
- Use Render Free tier for PostgreSQL (25MB, sleeps after inactivity)
- Use Render Free tier for Redis (25MB, sleeps)
- Use Render Free tier for Web Service (sleeps after 15 mins)
- Skip Background Worker or use Free tier
- **Total: $0/month** (but services sleep when idle)

---

## Monitoring & Logs

### Render Logs
- Dashboard → Service → **Logs** tab
- Real-time tail or historical search
- Filter by severity

### Netlify Logs
- Site → **Deploys** → Click deploy → **Deploy log**
- Function logs (if using Netlify Functions)

### Set Up Alerts (Optional)

**Render**:
1. Service → Settings → **Notifications**
2. Add email/Slack for deploy failures

**Netlify**:
1. Site settings → Build & deploy → **Deploy notifications**
2. Add email/Slack/webhook

---

## Troubleshooting

### Backend not starting
1. Render → Service → **Logs**
2. Common issues:
   - Missing env vars → Check Environment tab
   - Database connection → Verify `DATABASE_URL` uses internal hostname
   - Port binding → Render uses `PORT` env (should be 10000)

### Worker not processing tasks
1. Check worker logs for Redis connection
2. Verify `ENABLE_BACKGROUND_TASKS=true` on both API and worker
3. Restart worker: Render → Worker → **Manual Deploy** → Deploy latest commit

### Frontend not connecting to API
1. Check browser console for CORS errors
2. Verify `VITE_API_URL` in Netlify env vars
3. Test API directly: `curl https://codereview-api.onrender.com/api/health`

### GitHub webhooks not received
1. GitHub App → Advanced → Recent Deliveries
2. Check response codes (should be 200)
3. Verify webhook URL is correct
4. Check Render logs for webhook endpoint hits

---

## Scaling

### Increase Performance
- **Database**: Upgrade PostgreSQL plan (Render Dashboard)
- **Redis**: Upgrade to Standard ($10 → $30 for more memory)
- **API**: Increase instance count (1 → 2+) in Service settings
- **Worker**: Add more worker instances

### Add Staging Environment
1. Create separate Render services with `-staging` suffix
2. Deploy from `develop` branch
3. Use separate database/Redis instances
4. Point to staging Netlify deploy

---

## Rollback

### Render
1. Service → **Deploys** tab
2. Find previous successful deploy
3. Click **⋮** → **Redeploy**

### Netlify
1. Site → **Deploys**
2. Find previous deploy
3. Click **⋮** → **Publish deploy**

---

## Security Checklist

- [ ] All secrets stored in Render/Netlify env vars (not in code)
- [ ] GitHub webhook secret matches between GitHub App and `GITHUB_WEBHOOK_SECRET`
- [ ] JWT secret is strong (32+ character random hex)
- [ ] Database and Redis use internal URLs (not public)
- [ ] CORS is configured for your Netlify domain only
- [ ] GitHub App has minimal required permissions
- [ ] Render services are on latest Docker image

---

## Next Steps

1. ✅ **Monitor first webhook**: Open a PR and watch logs
2. ✅ **Set up custom domain** on Netlify (optional)
3. ✅ **Enable Render auto-deploy** (should be on by default)
4. ✅ **Add more repositories** to GitHub App
5. ✅ **Configure analysis rules** via `/api/config` endpoints

---

## Support Resources

- **Render Docs**: https://render.com/docs
- **Netlify Docs**: https://docs.netlify.com
- **Community**: GitHub Discussions on your repo
- **Logs**: Always check Render logs first for backend issues

---

**Deployment complete!** Your AI Code Review Assistant is now live and will automatically analyze all new pull requests.
