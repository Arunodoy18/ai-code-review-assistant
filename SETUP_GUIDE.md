# 🚀 Quick Start Guide

Complete setup guide for the AI Code Review Assistant.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [GitHub App Integration](#github-app-integration)
- [Deployment](#deployment)

---

## Prerequisites

### Required Software

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **PostgreSQL 15+** ([Download](https://www.postgresql.org/download/)) or SQLite for development
- **Redis** ([Download](https://redis.io/download/)) for Celery task queue

### Optional (for Docker deployment)

- **Docker & Docker Compose** ([Download](https://www.docker.com/get-started))

### API Keys

- **OpenAI API Key** (required for AI analysis) - Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Anthropic API Key** (optional alternative) - Get from [Anthropic Console](https://console.anthropic.com/)

---

## Installation

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd Project
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

---

## Configuration

### 1. Create Environment File

Copy the example and update with your credentials:

```bash
cp .env.example .env
```

### 2. Update .env File

**For Local Development (SQLite):**

```env
# Database - SQLite for local development
DATABASE_URL=sqlite:///./test.db

# GitHub App (use test values for now)
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY_PATH=./keys/test.pem
GITHUB_WEBHOOK_SECRET=test_secret

# LLM API - ADD YOUR REAL KEY
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=change-this-secret-in-production
```

**For Production (PostgreSQL):**

```env
DATABASE_URL=postgresql://user:password@localhost:5432/codereview_db
ENVIRONMENT=production
```

---

## Database Setup

### Option 1: Quick Setup (SQLite - Development)

```bash
cd backend

# Initialize database tables
python init_db.py

# Seed with test data
python seed_test_data.py
```

✅ This creates a `test.db` file with sample projects and analysis runs.

### Option 2: PostgreSQL (Production)

```bash
# Create database
createdb codereview_db

# Or using psql
psql -U postgres
CREATE DATABASE codereview_db;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/codereview_db

# Initialize tables
cd backend
python init_db.py
```

---

## Running the Application

### Option 1: Manual Start (Recommended for Development)

**Terminal 1 - Backend API:**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Celery Worker (Optional - for background jobs):**
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 4 - Redis (Optional - if not running as service):**
```bash
redis-server
```

### Option 2: Docker Compose (Production)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

---

## Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Interactive Swagger UI)

---

## GitHub App Integration

For webhook-based PR analysis, set up a GitHub App:

📚 **[Complete GitHub App Setup Guide](./GITHUB_APP_SETUP.md)**

**Quick Summary:**
1. Create GitHub App at https://github.com/settings/apps/new
2. Generate and download private key → save to `backend/keys/`
3. Update `.env` with App ID and webhook secret
4. Install app on repositories
5. Use ngrok for local webhook testing

---

## Deployment

### Deploy to Production

**Backend (FastAPI):**
- Deploy to: AWS EC2, Heroku, Azure App Service, DigitalOcean
- Use PostgreSQL for database
- Use Redis for Celery
- Set up SSL certificate

**Frontend (React):**
- Deploy to: Vercel, Netlify, AWS S3 + CloudFront
- Update `VITE_API_URL` to production backend URL

**Docker Compose (Full Stack):**
```bash
# Production compose file
docker-compose -f docker-compose.prod.yml up -d
```

---

## Verification

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-20T...",
  "service": "AI Code Review Assistant"
}
```

### 2. Check Database Connection

```bash
curl http://localhost:8000/api/ready
```

Expected response:
```json
{
  "status": "ready",
  "timestamp": "2025-12-20T...",
  "database": "connected"
}
```

### 3. View Test Data

Open http://localhost:5173 and you should see:
- 3 sample projects
- 5 analysis runs
- 40+ findings across multiple files

---

## Common Issues

### Backend won't start
- ✅ Check Python version: `python --version` (must be 3.10+)
- ✅ Activate virtual environment
- ✅ Install dependencies: `pip install -r requirements.txt`

### Frontend won't start
- ✅ Check Node version: `node --version` (must be 18+)
- ✅ Install dependencies: `npm install`
- ✅ Clear node_modules: `rm -rf node_modules && npm install`

### No data showing
- ✅ Run database initialization: `python init_db.py`
- ✅ Run seed data: `python seed_test_data.py`
- ✅ Check backend is running on port 8000

### API calls failing
- ✅ Check CORS settings in `backend/app/main.py`
- ✅ Verify `VITE_API_URL=http://localhost:8000` in frontend
- ✅ Check browser console for errors

---

## Next Steps

1. ✅ Add your OpenAI API key to `.env`
2. ✅ Set up GitHub App for real PR analysis
3. ✅ Configure analysis rules in `backend/app/services/analyzer_service.py`
4. ✅ Customize UI theme in `frontend/tailwind.config.js`
5. ✅ Add team members and configure access control

---

## Support

- 📖 [Full Documentation](./README.md)
- 🔧 [GitHub App Setup](./GITHUB_APP_SETUP.md)
- 🎨 [Frontend Development](./FRONTEND_COMPLETION_REPORT.md)
- ⚙️ [Backend Development](./DAY_2_PROGRESS_REPORT.md)

Happy coding! 🎉
