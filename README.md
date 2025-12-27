# AI-Powered Code Review Assistant 🤖

An intelligent, production-ready code review platform that uses machine learning and static analysis to automatically review pull requests, detect bugs, suggest optimizations, and enforce coding standards.

![Status](https://img.shields.io/badge/status-production--ready-brightgreen) ![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![React](https://img.shields.io/badge/react-18-blue) ![License](https://img.shields.io/badge/license-MIT-green)

## � One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/ai-code-review)

Deploy in 2 minutes with Railway - no DevOps experience needed! See [Railway Deployment Guide](RAILWAY_DEPLOYMENT.md).

## 📚 Documentation
- [**Railway Deployment**](RAILWAY_DEPLOYMENT.md) - One-click deploy to Railway (recommended).
- [**Distribution Guide**](DISTRIBUTION_GUIDE.md) - How to publish to GitHub, Vercel, and deliver to clients.
- [**Deployment Guide**](DEPLOYMENT.md) - Technical server configuration (AWS, DigitalOcean, Render).
- [**API Documentation**](backend/docs/api.md) - Backend API endpoints.

## ✨ Features

### 🤖 AI-Powered Analysis
- **LLM Integration**: GPT-4 and Claude for deep code understanding
- **Few-Shot Learning**: Context-aware analysis with example-based prompting
- **Smart Suggestions**: Actionable recommendations with code snippets

### 📋 Rule-Based Analysis
- **24 Comprehensive Rules**: Security, quality, performance, best practices
- **Multi-Language Support**: Python, JavaScript, TypeScript, Java
- **Custom Rules**: Easily extensible rule engine
- **Configuration UI**: Per-project rule enable/disable and severity overrides

### 🎯 Advanced Features
- **Diff-Aware**: Analyzes only changed code
- **Deduplication**: Smart finding consolidation
- **Severity Classification**: Critical, High, Medium, Low
- **Category Tagging**: Bug, Security, Performance, Style
- **GitHub Integration**: Seamless PR comments and status checks
- **Re-run Analysis**: Verify fixes with one click

### 📊 Modern Dashboard
- **Real-Time Updates**: Auto-refresh every 10 seconds
- **Interactive Filters**: By status, severity, category, time period
- **Rich Visualizations**: Gradient cards, color-coded severity
- **Detailed Views**: File-grouped findings with code snippets
- **Dark Mode**: System-wide theme with persistence
- **Responsive Design**: Mobile to desktop support

### ⚡ Performance & Production
- **Database Indexes**: 5-10x faster queries on key columns
- **API Caching**: 90% reduction in database load
- **Error Tracking**: Sentry integration for backend and frontend
- **Cloud Ready**: Deployment guides for Railway, Render, DigitalOcean
- **Docker Support**: Production-ready containers

## 🚀 Quick Start

### 📚 Complete Setup Guide

**👉 [Quick Start Guide](./SETUP_GUIDE.md)** - Complete installation and configuration

**👉 [GitHub App Setup](./GITHUB_APP_SETUP.md)** - Webhook integration guide

### ⚡ 60-Second Local Setup

```bash
# 1. Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install

# 2. Create database
cd ../backend
python init_db.py
python seed_test_data.py

# 3. Start backend (Terminal 1)
python -m uvicorn app.main:app --reload --port 8000

# 4. Start frontend (Terminal 2)
cd ../frontend
npm run dev

# 5. Open browser
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (modern, fast, async)
- **Database**: SQLAlchemy + PostgreSQL/SQLite
- **Task Queue**: Celery + Redis
- **AI/ML**: OpenAI API, Anthropic Claude
- **Analysis**: 24-rule engine + LLM service
- **Testing**: Pytest with comprehensive integration tests
- **Configuration**: JSON-based per-project rule management

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite (lightning-fast HMR)
- **Styling**: TailwindCSS (utility-first + dark mode)
- **State**: React Query (server state)
- **Routing**: React Router v6
- **Theme**: Dark/Light mode with persistence

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions ready
- **Deployment**: Railway, Render, DigitalOcean (guides included)
- **Monitoring**: Sentry error tracking
- **Performance**: Database indexes + API caching

## 📖 Documentation

- **[Setup Guide](./SETUP_GUIDE.md)** - Installation and configuration
- **[GitHub App Setup](./GITHUB_APP_SETUP.md)** - Webhook integration
- **[Deployment Guide](./DEPLOYMENT.md)** - Cloud deployment (Railway, Render, DigitalOcean)
- **[Sentry Setup](./SENTRY_SETUP.md)** - Error tracking configuration
- **[Demo Guide](./DEMO_GUIDE.md)** - Screenshots, videos, and demo workflows
- **[Custom Rules Guide](./CUSTOM_RULES_GUIDE.md)** - Create your own analysis rules
- **[Day 4 & 5 Report](./DAY_4_5_COMPLETION_REPORT.md)** - Latest features and optimizations
- **[Configuration & Testing (Day 3)](./DAY_3_PROGRESS_REPORT.md)** - Enterprise features
- **[Backend Report (Day 2)](./DAY_2_PROGRESS_REPORT.md)** - Analysis engine details
- **[Frontend Report](./FRONTEND_COMPLETION_REPORT.md)** - UI features and components

## 🏗️ Architecture

```
GitHub PR → Webhook → FastAPI → Celery Queue
                                     ↓
                         ┌──────────────────────┐
                         │  Analysis Pipeline   │
                         ├──────────────────────┤
                         │ 1. Fetch PR Diff     │
                         │ 2. Parse Changes     │
                         │ 3. Rule-Based Scan   │
                         │ 4. LLM Analysis      │
                         │ 5. Deduplication     │
                         └──────────────────────┘
                                     ↓
                    ┌────────────────┴────────────────┐
                    ↓                                  ↓
            PR Comments                          Dashboard
         (GitHub API)                        (PostgreSQL)
```

## 📊 Project Status

### ✅ Completed Features (100%)

#### Backend
- [x] FastAPI REST API with async support
- [x] 24 comprehensive analysis rules (security, quality, performance, best practices)
- [x] LLM integration (OpenAI GPT-4, Anthropic Claude)
- [x] Configuration management system (per-project rule settings)
- [x] 8 configuration API endpoints (enable/disable rules, severity overrides)
- [x] Advanced diff parsing and context extraction
- [x] Smart finding deduplication
- [x] Celery background task processing
- [x] GitHub App webhook handling
- [x] Database health checks with connectivity validation
- [x] Re-run analysis capability
- [x] SQLAlchemy models with performance indexes
- [x] Comprehensive test suite (15+ integration + webhook tests)
- [x] API response caching middleware
- [x] Sentry error tracking integration

#### Frontend
- [x] Modern React + TypeScript + TailwindCSS UI
- [x] Real-time dashboard with auto-refresh (10s)
- [x] Interactive severity and category filters
- [x] File-grouped findings display
- [x] Code snippets with syntax highlighting
- [x] Configuration UI (rule toggle, severity override, search)
- [x] Projects management page
- [x] Run details with metadata
- [x] Dark/Light mode with persistence
- [x] Responsive design (mobile to desktop)
- [x] Empty states and loading indicators
- [x] Sentry error tracking integration

#### Performance & Production
- [x] Database indexes on all key columns (5-10x faster queries)
- [x] API response caching (10s-10m TTL, 90% query reduction)
- [x] Cache invalidation on mutations
- [x] Performance monitoring with Sentry
- [x] Session replay for debugging

#### Infrastructure
- [x] Docker Compose setup (production-ready)
- [x] Database initialization and migration scripts
- [x] Test data seeding
- [x] Environment configuration
- [x] Cloud deployment guides (Railway, Render, DigitalOcean)
- [x] Comprehensive documentation (10+ guides)

### 🎯 Potential Enhancements

- [ ] Multi-repository dashboard
- [ ] Custom rule builder UI
- [ ] Team analytics and trends
- [ ] Slack/Discord notifications
- [ ] Code fix suggestions with diffs
- [ ] GitHub Actions integration
- [ ] SSO/SAML authentication
- [ ] Audit logs and compliance reports

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Anthropic for Claude API
- FastAPI for the amazing Python framework
- React team for the excellent frontend library
- TailwindCSS for utility-first styling

---

**Built with ❤️ by the AI Code Review Team**

*Making code reviews faster, smarter, and more consistent.*

## License

MIT
