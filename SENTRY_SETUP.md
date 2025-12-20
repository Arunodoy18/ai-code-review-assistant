# Sentry Error Tracking Setup

This guide covers setting up Sentry for error tracking in both the backend and frontend.

## Why Sentry?

Sentry provides:
- **Real-time error tracking** with stack traces
- **Performance monitoring** to identify slow endpoints
- **Session replay** to see what users experienced
- **Release tracking** to correlate errors with deployments
- **Alerts** for critical issues

## Getting Started

### 1. Create Sentry Account

1. Go to https://sentry.io
2. Sign up for free account (supports up to 5,000 errors/month)
3. Create a new organization

### 2. Create Projects

Create two projects:

#### Backend Project
- Platform: **Python**
- Name: `ai-code-review-backend`
- Copy the DSN (Data Source Name)

#### Frontend Project
- Platform: **React**
- Name: `ai-code-review-frontend`
- Copy the DSN

## Backend Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Sentry Error Tracking
SENTRY_DSN=https://[key]@[organization].ingest.sentry.io/[project_id]
SENTRY_TRACES_SAMPLE_RATE=0.1  # Sample 10% of transactions
ENVIRONMENT=production  # or development, staging
```

### Installation

Already included in `requirements.txt`:

```bash
pip install sentry-sdk[fastapi]==1.40.0
```

### Initialization

Sentry is automatically initialized in `app/main.py` if `SENTRY_DSN` is set.

### Testing

Test Sentry integration:

```python
# Test endpoint to trigger an error
import sentry_sdk

@router.get("/debug-sentry")
async def debug_sentry():
    sentry_sdk.capture_message("Test message from backend")
    raise Exception("This is a test error")
```

Visit the endpoint to trigger an error and verify it appears in Sentry dashboard.

## Frontend Configuration

### Environment Variables

Create `.env.local` or `.env.production`:

```bash
VITE_SENTRY_DSN=https://[key]@[organization].ingest.sentry.io/[project_id]
VITE_API_URL=https://your-backend.com
```

### Installation

Already included in `package.json`:

```bash
npm install @sentry/react
```

### Initialization

Sentry is automatically initialized in `src/main.tsx` if `VITE_SENTRY_DSN` is set.

### Error Boundaries

Wrap components with Sentry's ErrorBoundary:

```tsx
import * as Sentry from '@sentry/react';

function App() {
  return (
    <Sentry.ErrorBoundary fallback={<ErrorFallback />}>
      <YourApp />
    </Sentry.ErrorBoundary>
  );
}
```

### Testing

Test Sentry integration:

```tsx
// Add a test button
<button onClick={() => {
  throw new Error('Test Sentry error from frontend');
}}>
  Test Sentry
</button>
```

## Features

### Performance Monitoring

Backend performance monitoring is enabled by default. View:
- Slow database queries
- Slow API endpoints
- Transaction traces

### Session Replay (Frontend)

Records user sessions when errors occur. Helps debug:
- UI interactions leading to errors
- Network requests
- Console logs
- DOM mutations

### Release Tracking

Track which releases have errors:

#### Backend

```bash
# In deployment script
export SENTRY_RELEASE="backend@$(git rev-parse --short HEAD)"
sentry-cli releases new $SENTRY_RELEASE
sentry-cli releases set-commits $SENTRY_RELEASE --auto
sentry-cli releases finalize $SENTRY_RELEASE
```

#### Frontend

```bash
# In build script
export VITE_SENTRY_RELEASE="frontend@$(git rev-parse --short HEAD)"
npm run build
```

Update `vite.config.ts`:

```typescript
import { sentryVitePlugin } from "@sentry/vite-plugin";

export default defineConfig({
  plugins: [
    react(),
    sentryVitePlugin({
      org: "your-org",
      project: "ai-code-review-frontend",
      authToken: process.env.SENTRY_AUTH_TOKEN,
    }),
  ],
  build: {
    sourcemap: true,
  },
});
```

### Alerts

Configure alerts in Sentry dashboard:

1. **High Error Rate**: Alert when errors spike
2. **New Issues**: Notify on first occurrence of new errors
3. **Regressions**: Alert when previously resolved errors reappear
4. **Performance Degradation**: Alert on slow endpoints

Integrations available:
- Slack
- Email
- PagerDuty
- Discord
- Jira

## Best Practices

### Filtering Errors

Ignore known non-critical errors:

Backend (`app/main.py`):

```python
def before_send(event, hint):
    # Ignore specific errors
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        if isinstance(exc_value, IgnorableError):
            return None
    return event

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    before_send=before_send,
)
```

Frontend (`src/main.tsx`):

```typescript
Sentry.init({
  dsn: sentryDsn,
  beforeSend(event, hint) {
    // Filter out certain errors
    if (event.exception) {
      const error = hint.originalException;
      if (error instanceof NetworkError) {
        return null;
      }
    }
    return event;
  },
});
```

### Add Context

Add user context:

```python
# Backend
sentry_sdk.set_user({"id": user.id, "username": user.username})
```

```typescript
// Frontend
Sentry.setUser({ id: user.id, email: user.email });
```

Add custom context:

```python
# Backend
sentry_sdk.set_context("analysis", {
    "run_id": run.id,
    "pr_number": run.pr_number,
    "project": run.project.name
})
```

```typescript
// Frontend
Sentry.setContext('analysis', {
  runId: run.id,
  prNumber: run.prNumber,
});
```

### Performance Monitoring

Backend spans:

```python
import sentry_sdk

def analyze_code():
    with sentry_sdk.start_span(op="analysis", description="Code Analysis"):
        # Analysis logic
        with sentry_sdk.start_span(op="db", description="Fetch findings"):
            findings = db.query(Finding).all()
        
        with sentry_sdk.start_span(op="llm", description="LLM analysis"):
            result = llm.analyze(code)
```

Frontend custom transactions:

```typescript
import * as Sentry from '@sentry/react';

const transaction = Sentry.startTransaction({
  op: 'analysis.load',
  name: 'Load Analysis Run',
});

try {
  const data = await fetchAnalysis();
  transaction.setStatus('ok');
} catch (error) {
  transaction.setStatus('error');
  throw error;
} finally {
  transaction.finish();
}
```

## Troubleshooting

### Events Not Appearing

1. Check DSN is set correctly
2. Verify network connectivity to Sentry
3. Check Sentry quota limits (free tier: 5k errors/month)
4. Review `before_send` filters

### High Event Volume

1. Increase sampling rates:
   ```python
   traces_sample_rate=0.01  # 1% instead of 10%
   ```
2. Filter noisy errors
3. Upgrade Sentry plan

### Source Maps Not Working (Frontend)

1. Ensure `sourcemap: true` in vite.config.ts
2. Upload source maps using sentry-cli or Vite plugin
3. Verify release names match

## Cost Management

Free tier includes:
- 5,000 errors per month
- 10,000 performance units per month
- 50 replays per month
- 7 days retention

To stay within limits:
- Set appropriate sample rates
- Filter noisy errors
- Use issue grouping
- Archive resolved issues

## Resources

- [Sentry Python Docs](https://docs.sentry.io/platforms/python/)
- [Sentry React Docs](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Performance Monitoring](https://docs.sentry.io/product/performance/)
- [Session Replay](https://docs.sentry.io/product/session-replay/)
