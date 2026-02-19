# 🤖 AI Code Review SaaS Platform

> **Production-Ready SaaS Platform** for automated code review powered by advanced AI.  
> **Full monetization**, **enterprise security**, and **GDPR compliance** built-in.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)

---

## 🌟 Overview

A complete **Software-as-a-Service (SaaS)** platform that provides AI-powered code review for development teams. The platform analyzes pull requests using advanced language models, enforces security standards, tracks code quality metrics, and monetizes through a subscription-based business model.

**Current Status:** ✅ **Production Ready** - 100% market-ready with billing & compliance

**Revenue Model:** Freemium SaaS  
- **FREE:** $0/month (10 analyses)  
- **PRO:** $29/month (100 analyses)  
- **ENTERPRISE:** $99/month (unlimited)

---

## ✨ Features

### 🧠 AI-Powered Analysis (Phase 1-2)
- **Multi-LLM Support**: OpenAI GPT-4, Anthropic Claude, Google PaLM, Groq Llama
- **Full-Context Analysis**: Complete PR understanding with tree-sitter AST parsing
- **Semantic Code Search**: Vector embeddings for intelligent code navigation (pgvector)
- **Rule-Based + AI Detection**: Combined static analysis and ML insights
- **Code Sandbox**: Isolated Docker execution for security testing
- **Auto-Fix Suggestions**: AI-generated code corrections

### 🔐 Security & Compliance (Phase 3A)
- **Email Verification**: Secure account activation with token-based verification
- **Password Reset**: Forgot password flow with time-limited tokens
- **GDPR Compliance**: Full implementation of Articles 15 & 17
  - **Right to Access**: Export all user data (JSON download)
  - **Right to Erasure**: Complete account deletion
- **Security Hardening**:
  - HTTPS redirect middleware
  - Security headers (CSP, HSTS, X-Frame-Options)
  - Rate limiting (60 req/min default)
  - JWT authentication with bcrypt password hashing
- **Legal Pages**: Terms of Service & Privacy Policy

### 💳 Billing & Monetization (Phase 3B)
- **Stripe Integration**: Full payment processing with PCI compliance
- **Subscription Management**: 3-tier pricing (Free, Pro, Enterprise)
- **Usage Tracking**: Monthly analysis limits with enforcement
- **Billing Dashboard**: Self-service subscription management
- **14-Day Free Trial**: Risk-free trial for paid plans
- **Webhooks**: Real-time Stripe event processing
- **Revenue Analytics**: Usage statistics and billing insights

### 📊 Platform Features
- **Real-Time Dashboard**: Project metrics, analysis history, usage stats
- **GitHub Integration**: Automatic PR analysis via webhooks
- **Multi-Tenant Architecture**: Complete user isolation and data security
- **Background Tasks**: Celery + Redis for async processing
- **Error Tracking**: Sentry integration for production monitoring
- **Responsive UI**: Modern React with Tailwind CSS

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- **Framework**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL + SQLAlchemy ORM
- **Caching**: Redis
- **Task Queue**: Celery
- **Payment**: Stripe API
- **Email**: SMTP (aiosmtplib + Jinja2 templates)
- **AI/ML**: OpenAI, Anthropic, Google, Groq APIs
- **Search**: pgvector for semantic embeddings
- **Code Analysis**: tree-sitter (Python, JavaScript, TypeScript)
- **Security**: JWT, bcrypt, security middleware

**Frontend:**
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS
- **State**: Zustand + React Query
- **Build**: Vite
- **Routing**: React Router v6

**Infrastructure:**
- **Containers**: Docker + Docker Compose
- **Migrations**: Alembic
- **Error Tracking**: Sentry
- **Deployment**: Cloud Run, Azure, Render, Netlify

### Database Schema

```
users (multi-tenant)
├─ id, email, name
├─ hashed_password
├─ email_verified (Phase 3A)
├─ subscription_tier (Phase 3B)
└─ stripe_customer_id (Phase 3B)

subscriptions (Phase 3B)
├─ user_id
├─ tier (FREE, PRO, ENTERPRISE)
├─ status (ACTIVE, TRIALING, CANCELED)
├─ stripe_subscription_id
└─ trial_end

usage_tracking (Phase 3B)
├─ user_id, month
├─ analyses_used, analyses_limit
├─ total_lines_analyzed
└─ total_findings_generated

projects
├─ owner_id → users.id
└─ github_repo_full_name

analysis_runs
├─ project_id
├─ pr_number, pr_url
├─ status (PENDING, COMPLETED, FAILED)
└─ run_metadata (files analyzed, findings)

findings
├─ analysis_run_id
├─ severity (CRITICAL, HIGH, MEDIUM, LOW)
├─ category (SECURITY, PERFORMANCE, BUG)
└─ ai_generated_fix

email_verification_tokens (Phase 3A)
password_reset_tokens (Phase 3A)
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.10+** (with pip)
- **Node.js 18+** (with npm)
- **PostgreSQL 14+** (or SQLite for dev)
- **Redis 6+** (optional for local dev)
- **Docker** (optional)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/ai-code-review-saas.git
cd ai-code-review-saas
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (see Configuration section)

# Initialize database
python init_db.py

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload
```

Backend runs on **http://localhost:8000**  
API docs: **http://localhost:8000/docs**

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# Edit .env with VITE_API_URL=http://localhost:8000

# Start frontend
npm run dev
```

Frontend runs on **http://localhost:5173**

---

## ⚙️ Configuration

### Backend Environment Variables (`backend/.env`)

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/codereview
# Or for local dev: sqlite:///./local_dev.db

# Redis
REDIS_URL=redis://localhost:6379/0
ENABLE_BACKGROUND_TASKS=true

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI/LLM APIs (user can override with their own keys)
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
LLM_PROVIDER=groq

# GitHub Integration
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY_PATH=/path/to/private-key.pem
GITHUB_WEBHOOK_SECRET=your-webhook-secret
ENABLE_GITHUB_INTEGRATION=true
ENABLE_GITHUB_WEBHOOKS=true

# Email (Phase 3A)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@yourapp.com
ENABLE_EMAIL=true

# Stripe (Phase 3B)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_YEARLY_PRICE_ID=price_...
STRIPE_ENTERPRISE_MONTHLY_PRICE_ID=price_...
STRIPE_ENTERPRISE_YEARLY_PRICE_ID=price_...
ENABLE_BILLING=true

# Production
ENVIRONMENT=production
FRONTEND_URL=https://yourapp.com
SENTRY_DSN=https://...@sentry.io/...
```

### Frontend Environment Variables (`frontend/.env`)

```bash
VITE_API_URL=http://localhost:8000
# Production: VITE_API_URL=https://api.yourapp.com
```

---

## 📖 API Documentation

### Authentication

**Signup:**
```bash
POST /api/auth/signup
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
# Returns: JWT token + sends verification email
```

**Login:**
```bash
POST /api/auth/login
{
  "username": "user@example.com",
  "password": "SecurePass123!"
}
# Returns: { "access_token": "eyJ...", "token_type": "bearer" }
```

**Verify Email (Phase 3A):**
```bash
POST /api/auth/verify-email
{
  "token": "abc123..."
}
```

**Password Reset (Phase 3A):**
```bash
# Request reset
POST /api/auth/forgot-password
{
  "email": "user@example.com"
}

# Reset with token
POST /api/auth/reset-password
{
  "token": "xyz789...",
  "new_password": "NewSecurePass456!"
}
```

### Billing (Phase 3B)

**Get Plans:**
```bash
GET /api/billing/plans
# Returns: [{ tier, name, monthly_price, yearly_price, features }]
```

**Get Subscription:**
```bash
GET /api/billing/subscription
Authorization: Bearer <token>
# Returns: { tier, status, billing_interval, current_period_end }
```

**Create Checkout Session:**
```bash
POST /api/billing/subscription/checkout
Authorization: Bearer <token>
{
  "tier": "PRO",
  "billing_interval": "MONTHLY"
}
# Returns: { session_id, url } -> Redirect to Stripe Checkout
```

**Get Usage:**
```bash
GET /api/billing/usage
Authorization: Bearer <token>
# Returns: { analyses_used, analyses_limit, percentage_used }
```

### Code Analysis

**Analyze PR:**
```bash
POST /api/analysis/analyze-pr
Authorization: Bearer <token>
{
  "project_id": 1,
  "pr_number": 42
}
# Returns: { run_id, status, message }
```

**Get Analysis Results:**
```bash
GET /api/analysis/runs/{run_id}
Authorization: Bearer <token>
# Returns: { findings, pr_summary, run_metadata }
```

See full API documentation at **http://localhost:8000/docs** (Swagger UI)

---

## 💰 Pricing Strategy

| Tier | Price (Monthly) | Price (Yearly) | Analyses/Month | Target Audience |
|------|----------------|----------------|----------------|-----------------|
| **FREE** | $0 | $0 | 10 | Hobbyists, students |
| **PRO** | $29 | $290 (17% off) | 100 | Independent developers, small teams |
| **ENTERPRISE** | $99 | $990 (17% off) | Unlimited | Growing teams, companies |

**Revenue Projections (Year 1):**
- Month 1: $145 MRR (5 Pro users)
- Month 6: $1,747 MRR (50 Pro, 3 Enterprise)
- Month 12: $3,890 MRR (100 Pro, 10 Enterprise)
- **ARR:** ~$47,000 by end of Year 1

**Conversion Assumptions:**
- Free → Pro: 10%
- Pro → Enterprise: 5%
- Monthly Churn: 5%

---

## 🔧 Development Guide

### Project Structure

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   ├── auth.py              # Auth endpoints
│   │   ├── auth_phase3a.py      # Email verification, password reset
│   │   ├── billing.py           # Subscription & usage (Phase 3B)
│   │   ├── analysis.py          # Code analysis
│   │   └── ...
│   ├── services/         # Business logic
│   │   ├── llm_service.py       # AI integrations
│   │   ├── github_service.py    # GitHub API
│   │   ├── email_service.py     # Email templates (Phase 3A)
│   │   ├── stripe_service.py    # Billing (Phase 3B)
│   │   └── usage_service.py     # Usage tracking (Phase 3B)
│   ├── middleware/       # Middleware components
│   │   ├── cache.py             # Response caching
│   │   └── security.py          # Security headers (Phase 3A)
│   ├── models.py         # SQLAlchemy models
│   ├── config.py         # Settings management
│   └── main.py           # FastAPI app
├── alembic/              # Database migrations
│   └── versions/
│       ├── phase3a_security.py   # Email verification tables
│       └── phase3b_billing.py    # Subscription tables
└── requirements.txt

frontend/
├── src/
│   ├── api/              # API client
│   ├── components/       # Reusable components
│   │   ├── ErrorBoundary.tsx
│   │   ├── Layout.tsx
│   │   └── BillingDashboard.tsx  # Phase 3B
│   ├── pages/            # Route pages
│   │   ├── Login.tsx
│   │   ├── Signup.tsx
│   │   ├── Dashboard.tsx
│   │   ├── Projects.tsx
│   │   ├── Pricing.tsx           # Phase 3B
│   │   ├── TermsOfService.tsx    # Phase 3A
│   │   └── PrivacyPolicy.tsx     # Phase 3A
│   ├── contexts/         # React contexts
│   └── types/            # TypeScript types
└── package.json

docs/
├── PHASE_3A_SECURITY_LEGAL.md    # Email verification, GDPR
├── PHASE_3B_BILLING.md           # Stripe integration
├── MARKET_READY_ROADMAP.md       # Go-to-market strategy
└── DEPLOYMENT_GUIDE.md           # Production deployment
```

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 🚢 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Production Deployment (Cloud Run + Firebase)

**Step 1: Configure Stripe**
1. Create Stripe account → Get API keys
2. Create products: Pro ($29/mo), Enterprise ($99/mo)
3. Configure webhook: `https://api.yourapp.com/api/billing/webhooks/stripe`

**Step 2: Deploy Backend (Cloud Run)**
```bash
# Build & push image
docker build -t gcr.io/PROJECT_ID/backend ./backend
docker push gcr.io/PROJECT_ID/backend

# Deploy
gcloud run deploy backend \
  --image gcr.io/PROJECT_ID/backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=...,STRIPE_SECRET_KEY=..."
```

**Step 3: Deploy Frontend (Firebase Hosting)**
```bash
cd frontend
npm run build
firebase deploy
```

**Step 4: Configure Secrets**
- Store API keys in Google Secret Manager
- Configure environment variables in Cloud Run
- Set up Cloud SQL (PostgreSQL) and Redis (MemoryStore)

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for complete instructions.

---

## 📊 Monitoring & Analytics

### Error Tracking (Sentry)

```bash
# backend/.env
SENTRY_DSN=https://...@sentry.io/...
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### Stripe Dashboard
- **Payments**: Monitor revenue, failed payments
- **Subscriptions**: Track MRR, churn rate
- **Webhooks**: View event delivery logs

### Usage Analytics

```bash
GET /api/billing/usage/history?months=6
# Returns monthly usage trends
```

---

## 🛡️ Security

### Implemented Security Measures

✅ **Authentication**: JWT with bcrypt password hashing  
✅ **Email Verification**: Token-based account activation  
✅ **Rate Limiting**: 60 requests/minute per IP  
✅ **HTTPS Enforcement**: Automatic redirect in production  
✅ **Security Headers**: CSP, HSTS, X-Frame-Options, X-XSS-Protection  
✅ **GDPR Compliance**: Data export & deletion  
✅ **SQL Injection Protection**: SQLAlchemy ORM parameterized queries  
✅ **CSRF Protection**: SameSite cookies  
✅ **Secrets Management**: Environment variables (never committed)

### Production Security Checklist

- [ ] Change `JWT_SECRET_KEY` to cryptographically random value
- [ ] Enable HTTPS (Let's Encrypt, Cloudflare, or Cloud Load Balancer)
- [ ] Configure CORS for production frontend URL only
- [ ] Set up firewall rules (allow only 80/443)
- [ ] Enable database backups (automated daily)
- [ ] Configure Sentry for error monitoring
- [ ] Set up log aggregation (Cloud Logging, DataDog)
- [ ] Review Stripe webhook endpoint security
- [ ] Enable 2FA for admin accounts
- [ ] Conduct security audit before launch

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm run test

# E2E tests
npm run test:e2e
```

### Stripe Testing
Use Stripe test mode cards:
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **3D Secure**: `4000 0025 0000 3155`

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- **Python**: Follow PEP 8 (use `black` formatter)
- **TypeScript**: Follow ESLint rules (use `prettier`)

---

## 📚 Documentation

- **[Phase 3A: Security & Legal](docs/PHASE_3A_SECURITY_LEGAL.md)** - Email verification, GDPR compliance
- **[Phase 3B: Billing](docs/PHASE_3B_BILLING.md)** - Stripe integration, subscription management
- **[Market Roadmap](docs/MARKET_READY_ROADMAP.md)** - Go-to-market strategy
- **[Deployment Guide](docs/DEPLOYMENT_GUIDE.md)** - Production deployment instructions
- **[API Documentation](http://localhost:8000/docs)** - Interactive Swagger UI

---

## 🎯 Roadmap

### ✅ Phase 1: Core Features (COMPLETE)
- [x] Multi-LLM analysis (OpenAI, Anthropic, Google, Groq)
- [x] GitHub webhook integration
- [x] Real-time dashboard
- [x] Finding categorization

### ✅ Phase 2: Advanced Features (COMPLETE)
- [x] Semantic code search (pgvector)
- [x] Code sandbox (Docker isolation)
- [x] Auto-fix suggestions
- [x] Tree-sitter AST parsing

### ✅ Phase 3A: Security & Legal (COMPLETE)
- [x] Email verification system
- [x] Password reset flow
- [x] GDPR compliance (Articles 15 & 17)
- [x] Terms of Service & Privacy Policy
- [x] Security hardening

### ✅ Phase 3B: Billing & Monetization (COMPLETE)
- [x] Stripe integration
- [x] Subscription management
- [x] Usage tracking
- [x] Billing dashboard
- [x] 14-day free trial

### 🔄 Phase 3C: UX Polish (OPTIONAL - 1 week)
- [ ] Interactive onboarding flow
- [ ] In-app notifications
- [ ] Dark mode support
- [ ] Mobile-responsive improvements
- [ ] User preferences dashboard

### 🔄 Phase 3D: Operations (OPTIONAL - 1 week)
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Automated backups
- [ ] Health checks & alerts
- [ ] Production runbook

---

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check database connection
python init_db.py
```

**Frontend build fails:**
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

**Stripe webhook not receiving events:**
- Ensure webhook URL is publicly accessible
- Use ngrok for local testing: `ngrok http 8000`
- Verify webhook secret matches `.env` value
- Check Stripe Dashboard → Webhooks → Logs

**Email verification not working:**
- Verify SMTP credentials in `.env`
- Check spam folder for verification emails
- Enable "Less secure apps" for Gmail (or use app password)
- Test with Mailtrap or MailHog in development

**Usage limit not enforced:**
```bash
# Check subscription tier
GET /api/billing/subscription

# Verify usage tracking
GET /api/billing/usage

# Run migration if tables missing
alembic upgrade head
```

---

## 📧 Support

- **Documentation**: `/docs` folder
- **API Issues**: Check Swagger UI at `/docs`
- **Billing**: Stripe Dashboard or `support@yourapp.com`
- **Security**: `security@yourapp.com`

---

## 📄 License

This project is licensed under AGPL-3.0.
Commercial SaaS usage requires permission.
Attribution is required.

---

## 🌟 Acknowledgments

- **FastAPI** - Modern Python web framework
- **React** - UI library
- **Stripe** - Payment processing
- **OpenAI**, **Anthropic**, **Google**, **Groq** - AI providers
- **PostgreSQL** - Database
- **Redis** - Caching & task queue
- **Tailwind CSS** - Styling framework

---

**Built with ❤️ by developers, for developers**

**Ready to launch your SaaS?** This platform is 100% production-ready with enterprise security, GDPR compliance, and full monetization. Start generating revenue today!

🚀 **[Live Demo](https://demo.yourapp.com)** | 📘 **[Documentation](docs/)** | 💬 **[Discord Community](https://discord.gg/yourapp)**

