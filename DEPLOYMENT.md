# Deployment Guide

This guide covers deploying the AI Code Review Assistant to various cloud platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Railway Deployment](#railway-deployment)
- [Render Deployment](#render-deployment)
- [DigitalOcean App Platform](#digitalocean-app-platform)
- [Docker Deployment](#docker-deployment)
- [Production Checklist](#production-checklist)

## Prerequisites

Before deploying, ensure you have:

1. **GitHub App Credentials**
   - Follow [GITHUB_APP_SETUP.md](GITHUB_APP_SETUP.md) to create a GitHub App
   - Save the App ID, Private Key, and Webhook Secret

2. **LLM API Keys**
   - OpenAI API key (for GPT-4) or
   - Anthropic API key (for Claude)

3. **PostgreSQL Database**
   - Most platforms provide managed PostgreSQL
   - Or use external services like Supabase, Neon, or ElephantSQL

4. **Redis Instance** (optional but recommended)
   - For Celery task queue
   - Can use Upstash, Redis Cloud, or platform-provided Redis

## Environment Variables

All platforms require these environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# GitHub App
GITHUB_APP_ID=123456
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# LLM Provider
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=openai  # or anthropic

# Application
JWT_SECRET_KEY=your_secret_key_here_use_openssl_rand_hex_32
FRONTEND_URL=https://your-frontend-domain.com

# Celery (if using)
CELERY_BROKER_URL=redis://default:password@host:6379
CELERY_RESULT_BACKEND=redis://default:password@host:6379

# Optional
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## Railway Deployment

Railway offers the simplest deployment with automatic builds and zero-config infrastructure.

### Backend Deployment

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create New Project**
   ```bash
   railway init
   ```

3. **Add PostgreSQL**
   ```bash
   railway add postgresql
   ```

4. **Add Redis (optional)**
   ```bash
   railway add redis
   ```

5. **Configure Environment Variables**
   ```bash
   # Set via CLI
   railway variables set GITHUB_APP_ID=123456
   railway variables set OPENAI_API_KEY=sk-...
   
   # Or use the Railway dashboard: https://railway.app/project/[project-id]/variables
   ```

6. **Deploy Backend**
   ```bash
   cd backend
   railway up
   ```

7. **Run Database Migrations**
   ```bash
   railway run python init_db.py
   railway run python add_indexes.py
   ```

### Frontend Deployment

1. **Create Separate Service**
   ```bash
   cd frontend
   railway init
   ```

2. **Set Backend URL**
   ```bash
   railway variables set VITE_API_URL=https://your-backend.railway.app
   ```

3. **Deploy**
   ```bash
   railway up
   ```

### Scaling on Railway

- **Auto-scaling**: Railway automatically scales based on usage
- **Vertical scaling**: Adjust resources in project settings
- **Multiple replicas**: Available on Pro plan

**Estimated Cost**: $5-20/month for small projects, scales with usage

## Render Deployment

Render provides free tiers for testing and paid plans for production.

### Backend Deployment

1. **Create New Web Service**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Build Settings**
   - **Environment**: Python 3.11
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: Leave blank or set to `backend`

3. **Add PostgreSQL Database**
   - Create new PostgreSQL instance
   - Copy the Internal Database URL
   - Add as `DATABASE_URL` environment variable

4. **Add Redis** (optional)
   - Create Redis instance
   - Add connection URL as environment variables

5. **Set Environment Variables**
   - In web service settings, add all required variables
   - Use Render's "Environment Groups" for shared config

6. **Deploy**
   - Render automatically deploys on git push
   - Initial deployment takes 5-10 minutes

7. **Run Migrations**
   ```bash
   # Use Render Shell
   python init_db.py
   python add_indexes.py
   ```

### Frontend Deployment

1. **Create Static Site**
   - New Static Site from same repository
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`

2. **Environment Variables**
   ```bash
   VITE_API_URL=https://your-backend.onrender.com
   ```

3. **Custom Domain** (optional)
   - Add custom domain in settings
   - Configure DNS records

### Celery Worker on Render

1. **Create Background Worker**
   - New Background Worker service
   - **Build Command**: Same as web service
   - **Start Command**: `cd backend && celery -A app.tasks.celery_app worker --loglevel=info`

**Estimated Cost**: Free tier available, paid plans start at $7/month per service

## DigitalOcean App Platform

DigitalOcean App Platform offers managed containers with predictable pricing.

### Using App Spec

Create `app.yaml` in project root:

```yaml
name: ai-code-review
region: nyc

# Database
databases:
  - name: postgres
    engine: PG
    version: "15"
    size: db-s-1vcpu-1gb

# Backend API
services:
  - name: backend
    source:
      repo_clone_url: https://github.com/yourusername/ai-code-review.git
      branch: main
    dockerfile_path: backend/Dockerfile
    github:
      branch: main
      deploy_on_push: true
    
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${postgres.DATABASE_URL}
      - key: GITHUB_APP_ID
        scope: RUN_TIME
        value: "123456"
      - key: GITHUB_PRIVATE_KEY
        scope: RUN_TIME
        type: SECRET
      - key: GITHUB_WEBHOOK_SECRET
        scope: RUN_TIME
        type: SECRET
      - key: OPENAI_API_KEY
        scope: RUN_TIME
        type: SECRET
      - key: SECRET_KEY
        scope: RUN_TIME
        type: SECRET
      - key: FRONTEND_URL
        scope: RUN_TIME
        value: ${frontend.PUBLIC_URL}
    
    health_check:
      http_path: /api/health/liveness
    
    instance_count: 1
    instance_size_slug: basic-xs
    
    http_port: 8000

  # Celery Worker
  - name: celery-worker
    source:
      repo_clone_url: https://github.com/yourusername/ai-code-review.git
      branch: main
    dockerfile_path: backend/Dockerfile
    run_command: celery -A app.tasks.celery_app worker --loglevel=info
    
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${postgres.DATABASE_URL}
      # ... copy other envs from backend
    
    instance_count: 1
    instance_size_slug: basic-xs

# Frontend
static_sites:
  - name: frontend
    source:
      repo_clone_url: https://github.com/yourusername/ai-code-review.git
      branch: main
    
    build_command: cd frontend && npm install && npm run build
    output_dir: frontend/dist
    
    envs:
      - key: VITE_API_URL
        scope: BUILD_TIME
        value: ${backend.PUBLIC_URL}
    
    routes:
      - path: /
```

### Deploy

```bash
# Install doctl CLI
brew install doctl  # macOS
# or download from https://docs.digitalocean.com/reference/doctl/

# Authenticate
doctl auth init

# Create app
doctl apps create --spec app.yaml

# Or use web UI
# https://cloud.digitalocean.com/apps
```

**Estimated Cost**: $12-30/month depending on instance sizes

## Docker Deployment

For self-hosting or custom cloud providers.

### Using Docker Compose (Production)

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: codereviews
      POSTGRES_USER: codereviewer
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://codereviewer:${POSTGRES_PASSWORD}@postgres:5432/codereviews
      CELERY_BROKER_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      CELERY_RESULT_BACKEND: redis://:${REDIS_PASSWORD}@redis:6379/0
      GITHUB_APP_ID: ${GITHUB_APP_ID}
      GITHUB_PRIVATE_KEY: ${GITHUB_PRIVATE_KEY}
      GITHUB_WEBHOOK_SECRET: ${GITHUB_WEBHOOK_SECRET}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
      FRONTEND_URL: ${FRONTEND_URL}
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    restart: unless-stopped
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  celery:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://codereviewer:${POSTGRES_PASSWORD}@postgres:5432/codereviews
      CELERY_BROKER_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      CELERY_RESULT_BACKEND: redis://:${REDIS_PASSWORD}@redis:6379/0
      GITHUB_APP_ID: ${GITHUB_APP_ID}
      GITHUB_PRIVATE_KEY: ${GITHUB_PRIVATE_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    command: celery -A app.tasks.celery_app worker --loglevel=info

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        VITE_API_URL: ${BACKEND_URL}
    ports:
      - "80:80"
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Deploy

```bash
# Create .env file
cp .env.example .env.prod
# Edit .env.prod with production values

# Build and start
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec backend python init_db.py
docker-compose -f docker-compose.prod.yml exec backend python add_indexes.py

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Using Kubernetes

For advanced deployments, see example manifests in `/deploy/kubernetes/`.

## Production Checklist

### Security

- [ ] Use strong `SECRET_KEY` (min 32 characters)
- [ ] Enable HTTPS/TLS for all endpoints
- [ ] Store secrets in secure vault (AWS Secrets Manager, Railway Secrets, etc.)
- [ ] Rotate GitHub App private key periodically
- [ ] Enable CORS only for trusted domains
- [ ] Set up rate limiting
- [ ] Enable firewall rules

### Database

- [ ] Run migrations: `init_db.py` and `add_indexes.py`
- [ ] Enable automatic backups
- [ ] Set up connection pooling (SQLAlchemy defaults are good)
- [ ] Monitor query performance
- [ ] Set up database read replicas for scaling

### Monitoring

- [ ] Set up health check monitoring (use `/api/health/readiness`)
- [ ] Configure logging aggregation (Papertrail, Logtail, CloudWatch)
- [ ] Add error tracking (Sentry - see next section)
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure alerts for critical failures

### Performance

- [ ] Enable response caching (already configured)
- [ ] Use CDN for frontend (Cloudflare, CloudFront)
- [ ] Optimize database indexes (already configured)
- [ ] Configure Redis for Celery in production
- [ ] Set appropriate worker concurrency

### Scaling

- [ ] Configure horizontal pod autoscaling (if using K8s)
- [ ] Set up load balancer
- [ ] Monitor CPU and memory usage
- [ ] Add more Celery workers for heavy analysis load
- [ ] Consider database connection limits

### GitHub Integration

- [ ] Update GitHub App webhook URL to production domain
- [ ] Test webhook delivery from GitHub
- [ ] Set webhook secret in GitHub App settings
- [ ] Install app on target repositories

### Testing

- [ ] Run integration tests before deployment
- [ ] Verify all API endpoints
- [ ] Test GitHub webhook flow
- [ ] Verify LLM integration
- [ ] Test configuration management UI

## Troubleshooting

### Database Connection Issues

```bash
# Check DATABASE_URL format
# PostgreSQL: postgresql://user:password@host:5432/dbname
# SQLite (dev only): sqlite:///./test.db

# Test connection
python -c "from app.database import engine; engine.connect()"
```

### GitHub Webhook Not Working

1. Check webhook URL in GitHub App settings
2. Verify webhook secret matches
3. Check backend logs for webhook events
4. Use GitHub webhook delivery logs for debugging

### Celery Tasks Not Processing

1. Verify Redis/broker connection
2. Check Celery worker logs
3. Ensure worker is running: `celery -A app.tasks.celery_app inspect active`
4. Monitor task queue: `celery -A app.tasks.celery_app inspect reserved`

### High Memory Usage

1. Reduce Celery worker concurrency
2. Enable connection pooling
3. Optimize API response caching
4. Reduce LLM batch sizes

## Support

For deployment issues:
- Check application logs
- Review [README.md](README.md) and [SETUP_GUIDE.md](SETUP_GUIDE.md)
- Open GitHub issue with platform details

## Cost Optimization

- Start with smaller instance sizes and scale up
- Use managed PostgreSQL (cheaper than self-hosting)
- Use Redis for caching to reduce LLM calls
- Enable response caching to reduce database queries
- Monitor LLM API usage (largest cost factor)
- Use background jobs for expensive operations
