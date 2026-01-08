# AI Code Review Application

An intelligent code review system powered by AI that automatically analyzes pull requests and provides detailed feedback.

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
- **Database**: PostgreSQL
- **Caching**: Redis
- **Task Queue**: Celery
- **AI**: OpenAI API

### Frontend
- **Framework**: React + TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand + React Query
- **Build Tool**: Vite

## Prerequisites

- Docker & Docker Compose
- GitHub App credentials (for production)
- OpenAI API key

## Quick Start

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-name>
```

### 2. Set up environment variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://codereview:codereview_pass@postgres:5432/codereview_db

# GitHub App
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY_PATH=./keys/github-app-private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Redis
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET_KEY=your_secure_jwt_secret

# Environment
ENVIRONMENT=development
API_PORT=8000
FRONTEND_URL=http://localhost:5173
```

### 3. Run with Docker Compose

```bash
docker-compose up --build
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── middleware/   # Custom middleware
│   │   ├── schemas/      # Pydantic models
│   │   ├── services/     # Business logic
│   │   ├── tasks/        # Celery tasks
│   │   └── utils/        # Utility functions
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/   # React components
│   │   ├── contexts/     # React contexts
│   │   ├── pages/        # Page components
│   │   └── types/        # TypeScript types
│   ├── Dockerfile
│   └── package.json
│
└── docker-compose.yml
```

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Deployment

The application is designed to be deployed on Azure using:
- Azure Container Apps (for frontend and backend)
- Azure Database for PostgreSQL
- Azure Cache for Redis

Deployment configuration will be added in the next phase.

## License

MIT License
