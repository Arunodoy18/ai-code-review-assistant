# Quick Deployment Checklist

Use this checklist to get your AI Code Review Assistant production-ready.

## ☐ Step 1: Create GitHub App

1. Go to: https://github.com/settings/apps/new
2. Fill in the form:
   - **App name**: `ai-code-review-assistant-[your-name]` (must be unique)
   - **Homepage URL**: Your frontend URL (or http://localhost:5173 for testing)
   - **Webhook URL**: Leave blank for now (add ngrok URL later)
   - **Webhook secret**: Generate and save it!
   - **Permissions**:
     - Pull requests: Read & write
     - Contents: Read-only
     - Commit statuses: Read & write
   - **Subscribe to events**: Pull request, Pull request review
   - **Where to install**: Any account
3. Click **Create GitHub App**
4. **Note down**:
   - App ID (shown at top of page)
   - App slug/name (from URL)
5. Generate private key:
   - Scroll to "Private keys" section
   - Click "Generate a private key"
   - Download the .pem file
   - Move it to: `backend/keys/github-app-private-key.pem`

## ☐ Step 2: Update Code with Your App Details

After creating the GitHub App, update these files:

### File: `frontend/src/pages/Projects.tsx`
Replace `your-app-name` with your actual GitHub App slug in:
- Line ~60: Installation URL in "No projects" section
- Line ~147: Installation URL in "Manage installations" section

Example:
```typescript
// Change from:
href="https://github.com/apps/your-app-name/installations/new"
// To:
href="https://github.com/apps/ai-code-review-assistant-yourname/installations/new"
```

### File: `backend/.env`
Update these values:
```env
GITHUB_APP_ID=123456  # Your actual App ID
GITHUB_APP_PRIVATE_KEY_PATH=./keys/github-app-private-key.pem
GITHUB_WEBHOOK_SECRET=your_actual_webhook_secret
```

## ☐ Step 3: Get API Keys

### OpenAI (Required for AI analysis)
1. Go to: https://platform.openai.com/api-keys
2. Create new secret key
3. Add to `.env`:
   ```env
   OPENAI_API_KEY=sk-proj-...
   ```

### Anthropic (Optional, alternative to OpenAI)
1. Go to: https://console.anthropic.com/
2. Create API key
3. Add to `.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-...
   ```

## ☐ Step 4: Test Locally with Ngrok

1. Install ngrok: https://ngrok.com/download
2. Start your backend server:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload --port 8000
   ```
3. In another terminal, start ngrok:
   ```bash
   ngrok http 8000
   ```
4. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
5. Update GitHub App webhook URL:
   - Go to your GitHub App settings
   - Set Webhook URL to: `https://abc123.ngrok.io/api/webhooks/github`
   - Save changes

## ☐ Step 5: Install App on Test Repository

1. Go to: https://github.com/apps/YOUR-APP-NAME/installations/new
2. Select a test repository
3. Click Install
4. Create a test PR in that repository
5. Check your backend logs to see webhook received
6. Check frontend to see the analysis results

## ☐ Step 6: Deploy to Production

### Option A: Railway (Easiest)
1. Push code to GitHub
2. Go to: https://railway.app
3. Create new project from GitHub repo
4. Add environment variables from `.env.production.example`
5. Deploy!

### Option B: Render
1. Push code to GitHub
2. Go to: https://render.com
3. Create new Web Service
4. Connect GitHub repo, select `backend` folder
5. Add environment variables
6. Deploy!

### Option C: Docker (Any VPS)
1. Update `docker-compose.prod.yml` with your settings
2. Copy to your server
3. Run: `docker-compose -f docker-compose.prod.yml up -d`

### Frontend Deployment (Vercel)
1. Push to GitHub
2. Go to: https://vercel.com
3. Import repository
4. Set root directory to `frontend`
5. Add environment variable: `VITE_API_URL=your-backend-url`
6. Deploy!

## ☐ Step 7: Update Production URLs

After deployment, update:
1. GitHub App homepage URL → Your Vercel URL
2. GitHub App webhook URL → Your backend URL + `/api/webhooks/github`
3. Frontend `.env`: `VITE_API_URL=https://your-backend.railway.app`
4. Backend `.env`: `FRONTEND_URL=https://your-frontend.vercel.app`

## 🎉 You're Done!

Your AI Code Review Assistant is now live and ready to review pull requests!

### Next Steps:
- Share installation link with users: `https://github.com/apps/YOUR-APP-NAME`
- Monitor Sentry for errors (optional)
- Add custom rules in Configuration page
- Enjoy automated code reviews! 🚀
