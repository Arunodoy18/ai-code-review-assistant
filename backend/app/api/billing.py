"""Billing and subscription API endpoints (Phase 3B)."""
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.config import settings
from app.models import User, Subscription, SubscriptionTier, BillingInterval
from app.api.auth import get_current_user
from app.services.stripe_service import StripeService
from app.services.usage_service import UsageService
from pydantic import BaseModel

router = APIRouter(prefix="/api/billing", tags=["billing"])


# --- Request/Response Schemas ---

class SubscriptionPlanResponse(BaseModel):
    tier: str
    name: str
    monthly_price: int
    yearly_price: int
    analyses_limit: int
    features: list[str]


class CreateSubscriptionRequest(BaseModel):
    tier: str  # PRO or ENTERPRISE
    billing_interval: str  # MONTHLY or YEARLY
    trial: bool = True


class CheckoutSessionRequest(BaseModel):
    tier: str
    billing_interval: str


class SubscriptionResponse(BaseModel):
    id: int
    tier: str
    status: str
    billing_interval: Optional[str]
    current_period_start: Optional[str]
    current_period_end: Optional[str]
    cancel_at_period_end: bool
    trial_end: Optional[str]


class UsageStatsResponse(BaseModel):
    month: str
    analyses_used: int
    analyses_limit: int
    analyses_remaining: int
    percentage_used: int
    total_lines_analyzed: int
    total_findings_generated: int
    is_unlimited: bool


# --- API Endpoints ---

@router.get("/plans", response_model=list[SubscriptionPlanResponse])
async def get_subscription_plans():
    """Get all available subscription plans."""
    plans = []
    
    for tier in [SubscriptionTier.FREE, SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]:
        pricing = StripeService._get_pricing()[tier]
        
        # Define features for each tier
        if tier == SubscriptionTier.FREE:
            features = [
                "10 code analyses per month",
                "Basic AI feedback",
                "Public repositories only",
                "Community support",
            ]
        elif tier == SubscriptionTier.PRO:
            features = [
                "100 code analyses per month",
                "Advanced AI feedback",
                "Private repositories",
                "Priority support",
                "Custom analysis rules",
                "Detailed reports",
            ]
        else:  # ENTERPRISE
            features = [
                "Unlimited code analyses",
                "Premium AI feedback",
                "Private repositories",
                "24/7 dedicated support",
                "Custom analysis rules",
                "Advanced reports & analytics",
                "Team collaboration",
                "SSO integration",
            ]
        
        plans.append(SubscriptionPlanResponse(
            tier=tier.value,
            name=tier.value.capitalize(),
            monthly_price=pricing["monthly_price"],
            yearly_price=pricing["yearly_price"],
            analyses_limit=pricing["analyses_limit"],
            features=features,
        ))
    
    return plans


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's subscription."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        # Create default FREE subscription
        subscription = Subscription(
            user_id=current_user.id,
            tier=SubscriptionTier.FREE.value,
            status="ACTIVE",
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    return SubscriptionResponse(
        id=subscription.id,
        tier=subscription.tier,
        status=subscription.status,
        billing_interval=subscription.billing_interval,
        current_period_start=subscription.stripe_current_period_start.isoformat() if subscription.stripe_current_period_start else None,
        current_period_end=subscription.stripe_current_period_end.isoformat() if subscription.stripe_current_period_end else None,
        cancel_at_period_end=subscription.stripe_cancel_at_period_end,
        trial_end=subscription.trial_end.isoformat() if subscription.trial_end else None,
    )


@router.post("/subscription")
async def create_subscription(
    request: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new subscription for the user."""
    # Validate tier
    try:
        tier = SubscriptionTier(request.tier)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")
    
    # Validate billing interval
    try:
        billing_interval = BillingInterval(request.billing_interval)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid billing interval")
    
    # Check if user already has a subscription
    existing = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if existing and existing.tier != SubscriptionTier.FREE.value:
        raise HTTPException(status_code=400, detail="User already has an active subscription. Use upgrade/downgrade instead.")
    
    # Create subscription
    try:
        subscription = await StripeService.create_subscription(
            user=current_user,
            tier=tier,
            billing_interval=billing_interval,
            db=db,
            trial=request.trial,
        )
        
        return {
            "message": "Subscription created successfully",
            "subscription_id": subscription.id,
            "tier": subscription.tier,
            "status": subscription.status,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscription/checkout")
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a Stripe Checkout session for subscription purchase."""
    # Validate tier
    try:
        tier = SubscriptionTier(request.tier)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")
    
    # Validate billing interval
    try:
        billing_interval = BillingInterval(request.billing_interval)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid billing interval")
    
    # Cannot checkout for FREE tier
    if tier == SubscriptionTier.FREE:
        raise HTTPException(status_code=400, detail="Cannot checkout for FREE tier")
    
    # Ensure user has Stripe customer ID
    if not current_user.stripe_customer_id:
        await StripeService.create_customer(current_user, db)
    
    # Create checkout session
    try:
        session = await StripeService.create_checkout_session(
            user=current_user,
            tier=tier,
            billing_interval=billing_interval,
            success_url=f"{settings.frontend_url}/dashboard?subscription=success",
            cancel_url=f"{settings.frontend_url}/pricing?subscription=canceled",
        )
        
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscription/portal")
async def create_billing_portal_session(
    current_user: User = Depends(get_current_user),
):
    """Create a Stripe billing portal session for subscription management."""
    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No billing account found")
    
    try:
        session = await StripeService.create_billing_portal_session(
            user=current_user,
            return_url=f"{settings.frontend_url}/dashboard",
        )
        
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/subscription/cancel")
async def cancel_subscription(
    immediate: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cancel the user's subscription."""
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="No subscription found")
    
    if subscription.tier == SubscriptionTier.FREE.value:
        raise HTTPException(status_code=400, detail="Cannot cancel FREE subscription")
    
    try:
        subscription = await StripeService.cancel_subscription(
            subscription=subscription,
            db=db,
            immediate=immediate,
        )
        
        return {
            "message": "Subscription canceled successfully" if immediate else "Subscription will cancel at period end",
            "status": subscription.status,
            "cancel_at_period_end": subscription.stripe_cancel_at_period_end,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage", response_model=UsageStatsResponse)
async def get_usage_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current usage statistics for the user."""
    stats = UsageService.get_usage_stats(current_user, db)
    
    return UsageStatsResponse(**stats)


@router.get("/usage/history")
async def get_usage_history(
    months: int = 6,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get usage history for the last N months."""
    history = UsageService.get_monthly_usage_history(current_user, db, months)
    
    return {"history": history}


@router.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db),
):
    """Handle Stripe webhook events."""
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    # Get raw body
    payload = await request.body()
    
    # Verify and process webhook
    try:
        result = await StripeService.handle_webhook(payload, stripe_signature, db)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
