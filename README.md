# AI Code Review Application

An intelligent code review system powered by AI that automatically analyzes pull requests and provides detailed feedback.

> **Note:** This project is currently configured for local development only.  
> For deployment guides and production setup, see the `/docs/` folder.

## Features

- 🤖 AI-powered code analysis
- 📊 Real-time dashboard with project metrics
- 🔄 GitHub webhook integration
- 📈 Historical analysis tracking
- 🎨 Modern React frontend with Tailwind CSS
- ⚡ FastAPI backend with async support

## Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLite (local) / PostgreSQL (production)
- **Caching**: Redis (optional)
- **Task Queue**: Celery (optional)
- **AI**: OpenAI API

### Frontend
- **Framework**: React + TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand + React Query
- **Build Tool**: Vite

## Quick Start (Local Development)

### Prerequisites
- Node.js 18+
- npm
- Python 3.10+

SQLite is bundled with Python and used by default. PostgreSQL, Redis, Celery, and GitHub App credentials are optional for local runs and can be added later without code changes.

### 1. Backend (FastAPI)

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python init_db.py              # Creates local_dev.db SQLite file
uvicorn app.main:app --reload
```

The API listens on **http://localhost:8000** with zero external dependencies. Configuration lives in `backend/.env` and ships with sensible defaults:

```
DATABASE_URL=sqlite:///./local_dev.db
ENABLE_GITHUB_INTEGRATION=false
ENABLE_GITHUB_WEBHOOKS=false
ENABLE_BACKGROUND_TASKS=false
```

Enable GitHub or Redis features only when credentials and services are available by flipping the corresponding flags.

### 2. Frontend (Vite + React)

```bash
cd frontend
npm install
npm run dev
```

The dashboard is served on **http://localhost:5173** and points to the local API. If the backend is offline, the UI shows friendly empty states rather than crashing.

## Project Structure

```
├── backend/              # FastAPI backend (optional for UI demo)
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── services/    # Business logic
│   │   └── ...
│   └── requirements.txt
│
├── frontend/            # React frontend
│   ├── src/
│   │   ├── api/        # API client
│   │   ├── components/ # React components
│   │   ├── pages/      # Page components
│   │   └── ...
│   └── package.json
│
├── docs/               # Deployment guides and documentation
└── docker-compose.yml  # For full-stack local development
```

## Full-Stack Development

Running both services manually (as shown above) is the preferred local setup. A Docker workflow remains available for teams that want container parity:

```bash
docker-compose up --build
```

The compose file mounts the same local SQLite database and respects the `.env` flags, so you can toggle integrations without editing the containers.

## Preparing for Production (Firebase + Cloud Run)

- Build container images using the provided Dockerfiles for both backend and frontend.
- Store secrets in Google Secret Manager (OpenAI key, GitHub webhook secret, GitHub App private key). Inject the private key either as a mounted file or via the `GITHUB_APP_PRIVATE_KEY_B64` environment variable.
- Provision managed PostgreSQL (Cloud SQL) and Redis (MemoryStore) instances and set `DATABASE_URL` and `REDIS_URL` accordingly.
- Deploy the FastAPI image to Cloud Run with `ENABLE_GITHUB_INTEGRATION=true`, `ENABLE_GITHUB_WEBHOOKS=true`, and `ENABLE_BACKGROUND_TASKS=true`. Deploy a second Cloud Run service (or job) from the same image using the command `celery -A app.tasks.celery_app worker --loglevel=info`.
- Serve the compiled frontend via Firebase Hosting and configure rewrites so `/api/*` routes proxy to the Cloud Run backend.

See [docs/FIREBASE_DEPLOYMENT_GUIDE.md](docs/FIREBASE_DEPLOYMENT_GUIDE.md) for detailed steps.

## Deployment

For deployment instructions (Azure, Docker, CI/CD), see the `/docs/` folder:
- `PRODUCTION_DEPLOYMENT_GUIDE.md` - Complete production setup
- `DEPLOYMENT_GUIDE.md` - General deployment info
- Deployment scripts and configurations

## License

MIT License
