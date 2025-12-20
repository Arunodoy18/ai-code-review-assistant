# GitHub App Setup Guide

This guide walks you through setting up a GitHub App for webhook-based PR analysis.

## Prerequisites

- A GitHub account
- Admin access to repositories you want to analyze
- Your backend API running and accessible via a public URL (use ngrok for local development)

---

## Step 1: Create a GitHub App

1. Go to **GitHub Settings** → **Developer settings** → **GitHub Apps**
   - Direct link: https://github.com/settings/apps/new

2. Fill in the **Basic Information**:
   - **GitHub App name**: `AI Code Review Assistant` (must be unique)
   - **Homepage URL**: `http://localhost:5173` (or your frontend URL)
   - **Webhook URL**: `https://your-domain.com/api/webhooks/github` (use ngrok for local testing)
   - **Webhook secret**: Generate a strong secret (save this for .env)

3. Configure **Repository permissions**:
   - **Pull requests**: Read & write
   - **Contents**: Read-only
   - **Commit statuses**: Read & write
   - **Checks**: Read & write

4. Subscribe to **events**:
   - ✅ Pull request
   - ✅ Pull request review
   - ✅ Pull request review comment

5. Set **Where can this GitHub App be installed?**:
   - Choose "Only on this account" for personal use
   - Choose "Any account" to allow others to install it

6. Click **Create GitHub App**

---

## Step 2: Generate Private Key

1. After creating the app, scroll down to **Private keys** section
2. Click **Generate a private key**
3. A `.pem` file will download automatically
4. Move the file to `backend/keys/github-app-private-key.pem`

```bash
mkdir -p backend/keys
mv ~/Downloads/your-app-name.*.private-key.pem backend/keys/github-app-private-key.pem
```

---

## Step 3: Configure Environment Variables

Update your `.env` file with the GitHub App credentials:

```env
# GitHub App Configuration
GITHUB_APP_ID=123456                                    # From app settings page
GITHUB_APP_PRIVATE_KEY_PATH=./keys/github-app-private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here         # The secret you created
```

---

## Step 4: Install the App on Repositories

1. Go to your GitHub App settings page
2. Click **Install App** in the left sidebar
3. Select repositories to install on:
   - All repositories
   - Only select repositories
4. Click **Install**

Note: Save the **Installation ID** from the URL (e.g., `https://github.com/settings/installations/12345678`)

---

## Step 5: Setup Local Development with ngrok

For local testing, you need to expose your backend to the internet:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/download

# Start ngrok tunnel
ngrok http 8000
```

Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`) and update:
1. GitHub App webhook URL: `https://abc123.ngrok.io/api/webhooks/github`
2. Save settings

---

## Step 6: Test the Webhook

1. Create a test PR in an installed repository
2. Check backend logs for incoming webhook:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```
3. You should see: `INFO: Webhook received: pull_request.opened`

---

## Step 7: Verify Database Entry

After a PR is created, verify in your dashboard:

```bash
# Frontend
http://localhost:5173

# Backend API
http://localhost:8000/api/analysis/runs
```

---

## Troubleshooting

### Webhook not firing
- ✅ Check ngrok is running and URL is correct
- ✅ Verify webhook secret matches .env
- ✅ Check Recent Deliveries in GitHub App settings

### Authentication errors
- ✅ Verify GITHUB_APP_ID is correct
- ✅ Check private key file path and permissions
- ✅ Ensure installation ID is saved in database

### No analysis results
- ✅ Check OPENAI_API_KEY is set and valid
- ✅ Verify Celery worker is running: `celery -A app.tasks.celery_app worker`
- ✅ Check Redis is running: `redis-cli ping`

---

## Production Deployment

For production, replace ngrok with a permanent domain:

1. Deploy backend to cloud (AWS, Heroku, Azure, etc.)
2. Get SSL certificate (Let's Encrypt via Certbot)
3. Update GitHub App webhook URL to production domain
4. Use PostgreSQL instead of SQLite
5. Set strong production secrets in .env

---

## Security Best Practices

⚠️ **Never commit sensitive credentials to git**

```bash
# Add to .gitignore
.env
backend/keys/*.pem
```

✅ Use environment variables for all secrets
✅ Rotate webhook secrets periodically
✅ Restrict GitHub App permissions to minimum required
✅ Enable webhook secret validation in production

---

## Next Steps

- Configure analysis rules in `backend/app/services/analyzer_service.py`
- Customize LLM prompts in `backend/app/services/llm_service.py`
- Add custom finding categories
- Configure PR comment templates

Happy coding! 🚀
