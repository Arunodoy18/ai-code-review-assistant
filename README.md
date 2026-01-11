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
- **Database**: PostgreSQL
- **Caching**: Redis
- **Task Queue**: Celery
- **AI**: OpenAI API

### Frontend
- **Framework**: React + TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand + React Query
- **Build Tool**: Vite

## Quick Start (Local Development)

### Prerequisites
- Node.js 18+ and npm
- Python 3.9+
- PostgreSQL (optional - for backend)
- Redis (optional - for backend)

### Frontend Only

The simplest way to see the UI:

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at **http://localhost:5173**

> The backend is optional. If not running, API calls will fail gracefully without blocking the UI.

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

## Full-Stack Development (Optional)

If you want to run both frontend and backend locally:

### Option 1: Docker Compose

```bash
docker-compose up --build
```

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Deployment

For deployment instructions (Azure, Docker, CI/CD), see the `/docs/` folder:
- `PRODUCTION_DEPLOYMENT_GUIDE.md` - Complete production setup
- `DEPLOYMENT_GUIDE.md` - General deployment info
- Deployment scripts and configurations

## License

MIT License
