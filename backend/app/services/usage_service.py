"""Usage tracking service for billing limits."""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import User, UsageTracking, Subscription, SubscriptionTier
from app.services.stripe_service import StripeService


class UsageService:
    """Service for tracking and enforcing usage limits."""
    
    @staticmethod
    def get_current_month() -> str:
        """Get current month in YYYY-MM format."""
        return datetime.utcnow().strftime("%Y-%m")
    
    @staticmethod
    def get_or_create_usage_record(user: User, db: Session) -> UsageTracking:
        """Get or create usage record for current month."""
        current_month = UsageService.get_current_month()
        
        # Try to get existing record
        usage = db.query(UsageTracking).filter(
            UsageTracking.user_id == user.id,
            UsageTracking.month == current_month
        ).first()
        
        if not usage:
            # Create new record
            limit = UsageService.get_analyses_limit(user)
            usage = UsageTracking(
                user_id=user.id,
                month=current_month,
                analyses_used=0,
                analyses_limit=limit,
                total_lines_analyzed=0,
                total_findings_generated=0,
            )
            db.add(usage)
            db.commit()
            db.refresh(usage)
        
        return usage
    
    @staticmethod
    def get_analyses_limit(user: User) -> int:
        """Get analyses limit for user based on subscription tier."""
        tier = user.subscription_tier
        pricing = StripeService.PRICING.get(SubscriptionTier(tier))
        
        if not pricing:
            # Default to FREE tier
            return StripeService.PRICING[SubscriptionTier.FREE]["analyses_limit"]
        
        return pricing["analyses_limit"]
    
    @staticmethod
    def can_perform_analysis(user: User, db: Session) -> tuple[bool, Optional[str]]:
        """
        Check if user can perform an analysis.
        
        Returns:
            (can_perform, error_message)
        """
        usage = UsageService.get_or_create_usage_record(user, db)
        
        # Unlimited for enterprise
        if usage.analyses_limit == -1:
            return True, None
        
        # Check if limit reached
        if usage.analyses_used >= usage.analyses_limit:
            return False, f"Monthly analysis limit reached ({usage.analyses_limit}). Please upgrade your plan."
        
        return True, None
    
    @staticmethod
    def increment_usage(
        user: User,
        db: Session,
        lines_analyzed: int = 0,
        findings_generated: int = 0,
    ) -> UsageTracking:
        """Increment usage counters for the user."""
        usage = UsageService.get_or_create_usage_record(user, db)
        
        usage.analyses_used += 1
        usage.total_lines_analyzed += lines_analyzed
        usage.total_findings_generated += findings_generated
        
        db.commit()
        db.refresh(usage)
        
        return usage
    
    @staticmethod
    def get_usage_stats(user: User, db: Session) -> dict:
        """Get usage statistics for the user."""
        usage = UsageService.get_or_create_usage_record(user, db)
        
        # Calculate percentage
        if usage.analyses_limit == -1:
            percentage = 0  # Unlimited
            remaining = -1
        else:
            percentage = int((usage.analyses_used / usage.analyses_limit) * 100)
            remaining = usage.analyses_limit - usage.analyses_used
        
        return {
            "month": usage.month,
            "analyses_used": usage.analyses_used,
            "analyses_limit": usage.analyses_limit,
            "analyses_remaining": remaining,
            "percentage_used": percentage,
            "total_lines_analyzed": usage.total_lines_analyzed,
            "total_findings_generated": usage.total_findings_generated,
            "is_unlimited": usage.analyses_limit == -1,
        }
    
    @staticmethod
    def get_monthly_usage_history(user: User, db: Session, months: int = 6) -> list:
        """Get usage history for the last N months."""
        usage_records = db.query(UsageTracking).filter(
            UsageTracking.user_id == user.id
        ).order_by(
            UsageTracking.month.desc()
        ).limit(months).all()
        
        return [
            {
                "month": record.month,
                "analyses_used": record.analyses_used,
                "analyses_limit": record.analyses_limit,
                "total_lines_analyzed": record.total_lines_analyzed,
                "total_findings_generated": record.total_findings_generated,
            }
            for record in usage_records
        ]
    
    @staticmethod
    def reset_monthly_usage(db: Session):
        """
        Reset usage for a new month (run as cron job).
        This doesn't delete old records, just creates new ones.
        """
        current_month = UsageService.get_current_month()
        
        # Get all users who don't have a record for current month
        users_without_current_month = db.query(User).filter(
            ~User.id.in_(
                db.query(UsageTracking.user_id).filter(
                    UsageTracking.month == current_month
                )
            )
        ).all()
        
        # Create new records
        for user in users_without_current_month:
            limit = UsageService.get_analyses_limit(user)
            usage = UsageTracking(
                user_id=user.id,
                month=current_month,
                analyses_used=0,
                analyses_limit=limit,
                total_lines_analyzed=0,
                total_findings_generated=0,
            )
            db.add(usage)
        
        db.commit()
    
    @staticmethod
    def get_global_stats(db: Session) -> dict:
        """Get global usage statistics (admin only)."""
        current_month = UsageService.get_current_month()
        
        # Total analyses this month
        total_analyses = db.query(
            func.sum(UsageTracking.analyses_used)
        ).filter(
            UsageTracking.month == current_month
        ).scalar() or 0
        
        # Total users active this month
        active_users = db.query(
            func.count(UsageTracking.id)
        ).filter(
            UsageTracking.month == current_month,
            UsageTracking.analyses_used > 0
        ).scalar() or 0
        
        # Total lines analyzed
        total_lines = db.query(
            func.sum(UsageTracking.total_lines_analyzed)
        ).filter(
            UsageTracking.month == current_month
        ).scalar() or 0
        
        # Total findings generated
        total_findings = db.query(
            func.sum(UsageTracking.total_findings_generated)
        ).filter(
            UsageTracking.month == current_month
        ).scalar() or 0
        
        return {
            "month": current_month,
            "total_analyses": int(total_analyses),
            "active_users": int(active_users),
            "total_lines_analyzed": int(total_lines),
            "total_findings_generated": int(total_findings),
        }
