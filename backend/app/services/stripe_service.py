"""Stripe billing service for subscription management."""
import stripe
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import User, Subscription, SubscriptionTier, SubscriptionStatus, BillingInterval

settings = get_settings()
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Service for managing Stripe billing operations."""
    
    # Pricing configuration
    PRICING = {
        SubscriptionTier.FREE: {
            "monthly_price": 0,
            "yearly_price": 0,
            "analyses_limit": 10,
            "stripe_price_id_monthly": None,
            "stripe_price_id_yearly": None,
        },
        SubscriptionTier.PRO: {
            "monthly_price": 29,
            "yearly_price": 290,  # ~17% discount
            "analyses_limit": 100,
            "stripe_price_id_monthly": settings.STRIPE_PRO_MONTHLY_PRICE_ID,
            "stripe_price_id_yearly": settings.STRIPE_PRO_YEARLY_PRICE_ID,
        },
        SubscriptionTier.ENTERPRISE: {
            "monthly_price": 99,
            "yearly_price": 990,  # ~17% discount
            "analyses_limit": -1,  # Unlimited
            "stripe_price_id_monthly": settings.STRIPE_ENTERPRISE_MONTHLY_PRICE_ID,
            "stripe_price_id_yearly": settings.STRIPE_ENTERPRISE_YEARLY_PRICE_ID,
        },
    }
    
    TRIAL_DAYS = 14
    
    @staticmethod
    async def create_customer(user: User, db: Session) -> str:
        """Create a Stripe customer for the user."""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.name,
                metadata={
                    "user_id": user.id,
                    "environment": settings.ENVIRONMENT,
                }
            )
            
            # Update user with Stripe customer ID
            user.stripe_customer_id = customer.id
            db.commit()
            
            return customer.id
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create Stripe customer: {str(e)}")
    
    @staticmethod
    async def create_subscription(
        user: User,
        tier: SubscriptionTier,
        billing_interval: BillingInterval,
        db: Session,
        trial: bool = True,
    ) -> Subscription:
        """Create a new subscription for the user."""
        # Ensure user has a Stripe customer ID
        if not user.stripe_customer_id:
            await StripeService.create_customer(user, db)
        
        # Get pricing info
        pricing = StripeService.PRICING[tier]
        if billing_interval == BillingInterval.MONTHLY:
            price_id = pricing["stripe_price_id_monthly"]
        else:
            price_id = pricing["stripe_price_id_yearly"]
        
        if not price_id and tier != SubscriptionTier.FREE:
            raise ValueError(f"No price ID configured for {tier} {billing_interval}")
        
        # Create subscription in Stripe (if not FREE)
        stripe_subscription = None
        if tier != SubscriptionTier.FREE:
            try:
                subscription_params = {
                    "customer": user.stripe_customer_id,
                    "items": [{"price": price_id}],
                    "metadata": {
                        "user_id": user.id,
                        "tier": tier.value,
                    },
                }
                
                # Add trial period if requested
                if trial:
                    subscription_params["trial_period_days"] = StripeService.TRIAL_DAYS
                
                stripe_subscription = stripe.Subscription.create(**subscription_params)
            except stripe.error.StripeError as e:
                raise Exception(f"Failed to create Stripe subscription: {str(e)}")
        
        # Create subscription record in database
        subscription = Subscription(
            user_id=user.id,
            tier=tier.value,
            status=SubscriptionStatus.TRIALING.value if (trial and tier != SubscriptionTier.FREE) else SubscriptionStatus.ACTIVE.value,
            billing_interval=billing_interval.value if tier != SubscriptionTier.FREE else None,
            stripe_subscription_id=stripe_subscription.id if stripe_subscription else None,
            stripe_price_id=price_id,
            stripe_current_period_start=datetime.fromtimestamp(stripe_subscription.current_period_start) if stripe_subscription else None,
            stripe_current_period_end=datetime.fromtimestamp(stripe_subscription.current_period_end) if stripe_subscription else None,
            trial_start=datetime.utcnow() if trial else None,
            trial_end=datetime.utcnow() + timedelta(days=StripeService.TRIAL_DAYS) if trial else None,
        )
        
        db.add(subscription)
        
        # Update user subscription tier
        user.subscription_tier = tier.value
        if trial and tier != SubscriptionTier.FREE:
            user.trial_ends_at = subscription.trial_end
        
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    async def update_subscription(
        subscription: Subscription,
        new_tier: SubscriptionTier,
        new_billing_interval: BillingInterval,
        db: Session,
    ) -> Subscription:
        """Update an existing subscription (upgrade/downgrade)."""
        # Get new pricing info
        pricing = StripeService.PRICING[new_tier]
        if new_billing_interval == BillingInterval.MONTHLY:
            new_price_id = pricing["stripe_price_id_monthly"]
        else:
            new_price_id = pricing["stripe_price_id_yearly"]
        
        # Update in Stripe if moving to/from paid tier
        if subscription.stripe_subscription_id:
            if new_tier == SubscriptionTier.FREE:
                # Cancel paid subscription
                try:
                    stripe.Subscription.delete(subscription.stripe_subscription_id)
                    subscription.stripe_subscription_id = None
                    subscription.status = SubscriptionStatus.CANCELED.value
                    subscription.canceled_at = datetime.utcnow()
                except stripe.error.StripeError as e:
                    raise Exception(f"Failed to cancel Stripe subscription: {str(e)}")
            else:
                # Update subscription items
                try:
                    stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        items=[{
                            "id": stripe_sub["items"]["data"][0].id,
                            "price": new_price_id,
                        }],
                        proration_behavior="create_prorations",  # Prorate the change
                    )
                    
                    # Refresh subscription data
                    stripe_sub = stripe.Subscription.retrieve(subscription.stripe_subscription_id)
                    subscription.stripe_current_period_start = datetime.fromtimestamp(stripe_sub.current_period_start)
                    subscription.stripe_current_period_end = datetime.fromtimestamp(stripe_sub.current_period_end)
                except stripe.error.StripeError as e:
                    raise Exception(f"Failed to update Stripe subscription: {str(e)}")
        elif new_tier != SubscriptionTier.FREE:
            # Create new paid subscription
            user = subscription.user
            await StripeService.create_subscription(user, new_tier, new_billing_interval, db, trial=False)
            return subscription  # Return the new subscription
        
        # Update database record
        subscription.tier = new_tier.value
        subscription.billing_interval = new_billing_interval.value if new_tier != SubscriptionTier.FREE else None
        subscription.stripe_price_id = new_price_id
        
        # Update user tier
        subscription.user.subscription_tier = new_tier.value
        
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    async def cancel_subscription(subscription: Subscription, db: Session, immediate: bool = False) -> Subscription:
        """Cancel a subscription."""
        if subscription.stripe_subscription_id:
            try:
                if immediate:
                    # Cancel immediately
                    stripe.Subscription.delete(subscription.stripe_subscription_id)
                    subscription.status = SubscriptionStatus.CANCELED.value
                    subscription.canceled_at = datetime.utcnow()
                    subscription.user.subscription_tier = SubscriptionTier.FREE.value
                else:
                    # Cancel at period end
                    stripe.Subscription.modify(
                        subscription.stripe_subscription_id,
                        cancel_at_period_end=True,
                    )
                    subscription.stripe_cancel_at_period_end = True
            except stripe.error.StripeError as e:
                raise Exception(f"Failed to cancel Stripe subscription: {str(e)}")
        else:
            # Free tier, just mark as canceled
            subscription.status = SubscriptionStatus.CANCELED.value
            subscription.canceled_at = datetime.utcnow()
            subscription.user.subscription_tier = SubscriptionTier.FREE.value
        
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    @staticmethod
    async def create_checkout_session(
        user: User,
        tier: SubscriptionTier,
        billing_interval: BillingInterval,
        success_url: str,
        cancel_url: str,
    ) -> Dict[str, Any]:
        """Create a Stripe Checkout session for subscription signup."""
        # Ensure user has a Stripe customer ID
        if not user.stripe_customer_id:
            raise ValueError("User must have a Stripe customer ID")
        
        # Get pricing info
        pricing = StripeService.PRICING[tier]
        if billing_interval == BillingInterval.MONTHLY:
            price_id = pricing["stripe_price_id_monthly"]
        else:
            price_id = pricing["stripe_price_id_yearly"]
        
        try:
            session = stripe.checkout.Session.create(
                customer=user.stripe_customer_id,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                subscription_data={
                    "trial_period_days": StripeService.TRIAL_DAYS,
                    "metadata": {
                        "user_id": user.id,
                        "tier": tier.value,
                    },
                },
            )
            
            return {
                "session_id": session.id,
                "url": session.url,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create checkout session: {str(e)}")
    
    @staticmethod
    async def create_billing_portal_session(
        user: User,
        return_url: str,
    ) -> Dict[str, Any]:
        """Create a Stripe billing portal session for subscription management."""
        if not user.stripe_customer_id:
            raise ValueError("User must have a Stripe customer ID")
        
        try:
            session = stripe.billing_portal.Session.create(
                customer=user.stripe_customer_id,
                return_url=return_url,
            )
            
            return {
                "url": session.url,
            }
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create billing portal session: {str(e)}")
    
    @staticmethod
    async def handle_webhook(payload: bytes, signature: str, db: Session) -> Dict[str, Any]:
        """Handle Stripe webhook events."""
        try:
            event = stripe.Webhook.construct_event(
                payload,
                signature,
                settings.STRIPE_WEBHOOK_SECRET,
            )
        except ValueError:
            raise ValueError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise ValueError("Invalid signature")
        
        # Handle different event types
        event_type = event["type"]
        data = event["data"]["object"]
        
        if event_type == "customer.subscription.created":
            # New subscription created
            await StripeService._handle_subscription_created(data, db)
        elif event_type == "customer.subscription.updated":
            # Subscription updated
            await StripeService._handle_subscription_updated(data, db)
        elif event_type == "customer.subscription.deleted":
            # Subscription canceled
            await StripeService._handle_subscription_deleted(data, db)
        elif event_type == "invoice.payment_succeeded":
            # Payment succeeded
            await StripeService._handle_payment_succeeded(data, db)
        elif event_type == "invoice.payment_failed":
            # Payment failed
            await StripeService._handle_payment_failed(data, db)
        
        return {"status": "success", "event_type": event_type}
    
    @staticmethod
    async def _handle_subscription_created(data: Dict[str, Any], db: Session):
        """Handle subscription.created webhook."""
        subscription_id = data["id"]
        user_id = int(data["metadata"].get("user_id"))
        
        # Update subscription in database
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_id
        ).first()
        
        if subscription:
            subscription.status = data["status"].upper()
            subscription.stripe_current_period_start = datetime.fromtimestamp(data["current_period_start"])
            subscription.stripe_current_period_end = datetime.fromtimestamp(data["current_period_end"])
            db.commit()
    
    @staticmethod
    async def _handle_subscription_updated(data: Dict[str, Any], db: Session):
        """Handle subscription.updated webhook."""
        subscription_id = data["id"]
        
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_id
        ).first()
        
        if subscription:
            subscription.status = data["status"].upper()
            subscription.stripe_current_period_start = datetime.fromtimestamp(data["current_period_start"])
            subscription.stripe_current_period_end = datetime.fromtimestamp(data["current_period_end"])
            subscription.stripe_cancel_at_period_end = data.get("cancel_at_period_end", False)
            db.commit()
    
    @staticmethod
    async def _handle_subscription_deleted(data: Dict[str, Any], db: Session):
        """Handle subscription.deleted webhook."""
        subscription_id = data["id"]
        
        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_id
        ).first()
        
        if subscription:
            subscription.status = SubscriptionStatus.CANCELED.value
            subscription.canceled_at = datetime.utcnow()
            subscription.user.subscription_tier = SubscriptionTier.FREE.value
            db.commit()
    
    @staticmethod
    async def _handle_payment_succeeded(data: Dict[str, Any], db: Session):
        """Handle invoice.payment_succeeded webhook."""
        subscription_id = data.get("subscription")
        
        if subscription_id:
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_id
            ).first()
            
            if subscription and subscription.status == SubscriptionStatus.PAST_DUE.value:
                subscription.status = SubscriptionStatus.ACTIVE.value
                db.commit()
    
    @staticmethod
    async def _handle_payment_failed(data: Dict[str, Any], db: Session):
        """Handle invoice.payment_failed webhook."""
        subscription_id = data.get("subscription")
        
        if subscription_id:
            subscription = db.query(Subscription).filter(
                Subscription.stripe_subscription_id == subscription_id
            ).first()
            
            if subscription:
                subscription.status = SubscriptionStatus.PAST_DUE.value
                db.commit()
