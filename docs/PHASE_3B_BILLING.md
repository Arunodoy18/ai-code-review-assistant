# Phase 3B: Billing & Monetization - Complete Implementation

## Overview
Phase 3B transforms your AI Code Review platform into a revenue-generating SaaS product by implementing:
- ✅ Stripe payment integration
- ✅ Three-tier subscription system (Free, Pro, Enterprise)
- ✅ Usage tracking and limit enforcement
- ✅ Billing dashboard and management
- ✅ Webhook handling for Stripe events
- ✅ 14-day free trial for paid plans

## Architecture

### Database Models

#### 1. Subscription Table
```sql
CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL,
    tier VARCHAR NOT NULL,  -- FREE, PRO, ENTERPRISE
    status VARCHAR NOT NULL,  -- ACTIVE, TRIALING, PAST_DUE, CANCELED
    billing_interval VARCHAR,  -- MONTHLY, YEARLY
    stripe_subscription_id VARCHAR UNIQUE,
    stripe_price_id VARCHAR,
    stripe_current_period_start TIMESTAMP,
    stripe_current_period_end TIMESTAMP,
    stripe_cancel_at_period_end BOOLEAN DEFAULT FALSE,
    trial_start TIMESTAMP,
    trial_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    canceled_at TIMESTAMP
);
```

#### 2. UsageTracking Table
```sql
CREATE TABLE usage_tracking (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    month VARCHAR NOT NULL,  -- Format: "2024-01"
    analyses_used INTEGER DEFAULT 0,
    analyses_limit INTEGER NOT NULL,
    total_lines_analyzed INTEGER DEFAULT 0,
    total_findings_generated INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, month)
);
```

#### 3. User Table Extensions
```sql
ALTER TABLE users ADD COLUMN subscription_tier VARCHAR DEFAULT 'FREE';
ALTER TABLE users ADD COLUMN stripe_customer_id VARCHAR UNIQUE;
ALTER TABLE users ADD COLUMN trial_ends_at TIMESTAMP;
```

### Pricing Tiers

| Tier | Monthly | Yearly | Analyses/Month | Features |
|------|---------|--------|----------------|----------|
| **FREE** | $0 | $0 | 10 | Basic AI feedback, Public repos, Community support |
| **PRO** | $29 | $290 (~17% off) | 100 | Advanced AI, Private repos, Priority support, Custom rules |
| **ENTERPRISE** | $99 | $990 (~17% off) | Unlimited | Premium AI, 24/7 support, Team collaboration, SSO |

## Backend Implementation

### 1. Stripe Service (`backend/app/services/stripe_service.py`)

**Key Features:**
- Create Stripe customers
- Manage subscriptions (create, update, cancel)
- Handle checkout sessions
- Process webhooks

**Configuration Required:**
```bash
# .env
STRIPE_SECRET_KEY=sk_test_...  # From Stripe Dashboard
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...  # From Stripe webhook config

# Price IDs (create in Stripe Dashboard)
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_YEARLY_PRICE_ID=price_...
STRIPE_ENTERPRISE_MONTHLY_PRICE_ID=price_...
STRIPE_ENTERPRISE_YEARLY_PRICE_ID=price_...

ENABLE_BILLING=true
```

### 2. Usage Service (`backend/app/services/usage_service.py`)

**Key Features:**
- Track API usage per user per month
- Enforce subscription limits
- Provide usage statistics
- Reset monthly usage (cron job)

**Usage Enforcement Pattern:**
```python
# Before analysis
can_analyze, error_msg = UsageService.can_perform_analysis(current_user, db)
if not can_analyze:
    raise HTTPException(status_code=403, detail=error_msg)

# After successful analysis
UsageService.increment_usage(
    user=current_user,
    db=db,
    lines_analyzed=total_lines,
    findings_generated=len(findings),
)
```

### 3. Billing API (`backend/app/api/billing.py`)

**Endpoints:**

```bash
# Plans
GET  /api/billing/plans  # Get all subscription plans

# Subscription Management
GET  /api/billing/subscription  # Get current subscription
POST /api/billing/subscription  # Create subscription
POST /api/billing/subscription/checkout  # Create Stripe checkout session
POST /api/billing/subscription/portal  # Open Stripe billing portal
POST /api/billing/subscription/cancel?immediate=false  # Cancel subscription

# Usage Tracking
GET  /api/billing/usage  # Get current usage stats
GET  /api/billing/usage/history?months=6  # Get usage history

# Webhooks
POST /api/billing/webhooks/stripe  # Stripe webhook handler
```

## Frontend Implementation

### 1. Pricing Page (`frontend/src/pages/Pricing.tsx`)

**Features:**
- Display all subscription plans
- Monthly/Yearly billing toggle (shows 17% savings)
- Plan comparison table
- FAQ section
- Redirect to Stripe Checkout

**Usage:**
```tsx
import { PricingPage } from './pages/Pricing';

// In your router
<Route path="/pricing" element={<PricingPage />} />
```

### 2. Billing Dashboard (`frontend/src/components/BillingDashboard.tsx`)

**Features:**
- View current subscription details
- Monitor usage (visual progress bar)
- Manage billing via Stripe portal
- Cancel subscription
- Upgrade/downgrade plans
- Usage warnings (at 90% limit)

**Usage:**
```tsx
import { BillingDashboard } from './components/BillingDashboard';

// In your dashboard
<Route path="/billing" element={<BillingDashboard />} />
```

## Setup Instructions

### Step 1: Install Stripe SDK

```bash
cd backend
pip install stripe==8.0.0
```

### Step 2: Configure Stripe

1. **Create Stripe Account:**
   - Go to https://stripe.com
   - Sign up for free account
   - Get API keys from Dashboard → Developers → API keys

2. **Create Products & Prices:**
   ```bash
   # Go to Stripe Dashboard → Products
   
   # PRO Plan
   - Name: "Pro"
   - Monthly Price: $29/month (ID: price_XXX)
   - Yearly Price: $290/year (ID: price_YYY)
   
   # ENTERPRISE Plan
   - Name: "Enterprise"
   - Monthly Price: $99/month (ID: price_ZZZ)
   - Yearly Price: $990/year (ID: price_AAA)
   ```

3. **Configure Webhooks:**
   ```bash
   # Stripe Dashboard → Developers → Webhooks → Add endpoint
   
   Endpoint URL: https://your-domain.com/api/billing/webhooks/stripe
   
   Events to listen for:
   - customer.subscription.created
   - customer.subscription.updated
   - customer.subscription.deleted
   - invoice.payment_succeeded
   - invoice.payment_failed
   
   # Copy the signing secret (whsec_...)
   ```

4. **Environment Variables:**
   ```bash
   # backend/.env
   STRIPE_SECRET_KEY=sk_test_51...
   STRIPE_PUBLISHABLE_KEY=pk_test_51...
   STRIPE_WEBHOOK_SECRET=whsec_...
   STRIPE_PRO_MONTHLY_PRICE_ID=price_1...
   STRIPE_PRO_YEARLY_PRICE_ID=price_2...
   STRIPE_ENTERPRISE_MONTHLY_PRICE_ID=price_3...
   STRIPE_ENTERPRISE_YEARLY_PRICE_ID=price_4...
   ENABLE_BILLING=true
   ```

### Step 3: Run Database Migration

```bash
cd backend
alembic upgrade head
```

This creates:
- `subscriptions` table
- `usage_tracking` table
- Adds subscription fields to `users` table
- Creates default FREE subscriptions for existing users

### Step 4: Test the Integration

**Backend Test (curl):**
```bash
# Get subscription plans
curl -X GET http://localhost:8000/api/billing/plans

# Get current subscription (requires auth)
curl -X GET http://localhost:8000/api/billing/subscription \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get usage stats
curl -X GET http://localhost:8000/api/billing/usage \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create checkout session
curl -X POST http://localhost:8000/api/billing/subscription/checkout \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"tier": "PRO", "billing_interval": "MONTHLY"}'
```

**Frontend Test:**
```bash
cd frontend
npm install
npm run dev

# Navigate to:
http://localhost:5173/pricing  # View plans
http://localhost:5173/billing  # Manage subscription
```

## Stripe Webhook Testing

### Local Development (Stripe CLI)

1. **Install Stripe CLI:**
   ```bash
   # Windows
   scoop install stripe
   
   # Mac
   brew install stripe/stripe-cli/stripe
   ```

2. **Login & Forward Webhooks:**
   ```bash
   stripe login
   
   stripe listen --forward-to localhost:8000/api/billing/webhooks/stripe
   # Copy the webhook signing secret (whsec_...) to .env
   ```

3. **Trigger Test Events:**
   ```bash
   # Test subscription created
   stripe trigger customer.subscription.created
   
   # Test payment succeeded
   stripe trigger invoice.payment_succeeded
   
   # Test payment failed
   stripe trigger invoice.payment_failed
   ```

## Usage Limit Enforcement

The system automatically enforces limits on the `/api/analysis/analyze-pr` endpoint:

```python
# In backend/app/api/analysis.py

# Phase 3B: Check usage limits
from app.services.usage_service import UsageService

can_analyze, error_msg = UsageService.can_perform_analysis(current_user, db)
if not can_analyze:
    raise HTTPException(status_code=403, detail=error_msg)

# After successful analysis
UsageService.increment_usage(
    user=current_user,
    db=db,
    lines_analyzed=total_lines,
    findings_generated=len(findings),
)
```

**Response when limit reached:**
```json
{
  "detail": "Monthly analysis limit reached (10). Please upgrade your plan."
}
```

## Monthly Reset (Production)

Set up a cron job to reset monthly usage:

```bash
# crontab -e
0 0 1 * * curl -X POST http://localhost:8000/api/billing/reset-usage
```

Or use a cloud scheduler (AWS EventBridge, GCP Cloud Scheduler, etc.)

## Revenue Projections

**Year 1 Conservative Estimates:**

| Month | Free Users | Pro Users | Ent Users | MRR |
|-------|-----------|-----------|-----------|-----|
| Month 1 | 50 | 5 ($145) | 0 | $145 |
| Month 3 | 150 | 20 ($580) | 1 ($99) | $679 |
| Month 6 | 300 | 50 ($1,450) | 3 ($297) | $1,747 |
| Month 12 | 600 | 100 ($2,900) | 10 ($990) | $3,890 |

**Conversion Rate Assumptions:**
- Free → Pro: 10%
- Pro → Enterprise: 5%
- Churn Rate: 5% monthly

**ARR Projection:** ~$47,000 by end of Year 1

## Security Best Practices

1. **Never log Stripe keys** in application logs
2. **Verify webhook signatures** using `stripe.Webhook.construct_event()`
3. **Use HTTPS** in production for webhook endpoints
4. **Rotate API keys** if compromised
5. **Monitor webhook failures** in Stripe Dashboard
6. **Implement idempotency** for critical operations

## Troubleshooting

### "No price ID configured" Error
- Ensure all `STRIPE_*_PRICE_ID` environment variables are set
- Check that price IDs match exactly from Stripe Dashboard

### Webhook Not Receiving Events
- Verify webhook endpoint is publicly accessible (use ngrok for local testing)
- Check webhook signing secret matches `.env` value
- Review Stripe Dashboard → Webhooks for delivery logs

### "User must have a Stripe customer ID" Error
- Customer is created automatically on first subscription attempt
- Manually trigger: `StripeService.create_customer(user, db)`

### Payment Declined
- Test mode: Use Stripe test cards (4242 4242 4242 4242)
- Live mode: Check customer's payment method in Stripe Dashboard

## Next Steps

After Phase 3B completion, consider:
- **Phase 3C:** UX Polish (onboarding flow, notifications, dark mode)
- **Phase 3D:** Operations (monitoring, backups, production deployment)
- **Add-ons:** Team accounts, annual discounts, enterprise SSO

## Support

For billing issues:
- **Code:** `backend/app/api/billing.py`, `backend/app/services/stripe_service.py`
- **Stripe Logs:** Stripe Dashboard → Developers → Logs
- **Webhook Logs:** Stripe Dashboard → Webhooks → [Your endpoint]

---

**Phase 3B Status:** ✅ **COMPLETE** - Platform is now revenue-ready!

**Estimated Setup Time:** 2-3 hours  
**Monthly Revenue Potential:** $400+ (Month 1) → $4,000+ (Month 12)
