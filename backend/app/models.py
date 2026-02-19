from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum, Boolean, Float, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
import enum
from app.database import Base


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class FindingSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FindingCategory(str, enum.Enum):
    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    BEST_PRACTICE = "best_practice"
    DOCUMENTATION = "documentation"


# Phase 3B: Billing & Monetization Enums

class SubscriptionTier(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


class BillingInterval(str, enum.Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False, index=True)  # Phase 3A: Email verification
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Per-user LLM API keys (SaaS: users bring their own keys)
    groq_api_key = Column(String, nullable=True)
    openai_api_key = Column(String, nullable=True)
    anthropic_api_key = Column(String, nullable=True)
    google_api_key = Column(String, nullable=True)
    preferred_llm_provider = Column(String, default="groq")

    # GitHub integration (SaaS: users provide their own PAT)
    github_token = Column(String, nullable=True)
    github_webhook_secret = Column(String, nullable=True)  # Per-user webhook secret

    # Phase 3B: Billing & Subscriptions
    subscription_tier = Column(String, default="FREE", nullable=False, index=True)  # FREE, PRO, ENTERPRISE
    stripe_customer_id = Column(String, unique=True, nullable=True, index=True)
    trial_ends_at = Column(DateTime, nullable=True)  # Free trial period
    
    projects = relationship("Project", back_populates="owner")
    subscription = relationship("Subscription", back_populates="user", uselist=False)  # One-to-one
    usage_records = relationship("UsageTracking", back_populates="user")


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint('github_repo_full_name', 'owner_id', name='uq_project_repo_owner'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    github_repo_full_name = Column(String, nullable=False, index=True)  # owner/repo
    github_installation_id = Column(Integer, nullable=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    config = Column(JSON, default={})  # Rules, thresholds, etc.
    dismissed_patterns = Column(JSON, default=[])  # Learned false-positive patterns
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="projects")
    runs = relationship("AnalysisRun", back_populates="project")


class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    pr_number = Column(Integer, nullable=False, index=True)
    pr_url = Column(String, nullable=False)
    pr_title = Column(String)
    pr_author = Column(String, index=True)
    base_sha = Column(String, nullable=False)
    head_sha = Column(String, nullable=False, index=True)
    status = Column(SQLEnum(RunStatus), default=RunStatus.PENDING, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True, index=True)
    error_message = Column(Text, nullable=True)
    run_metadata = Column(JSON, default={})  # Changed files count, lines analyzed, etc.
    risk_score = Column(Float, nullable=True)  # 0-100 PR risk score
    risk_breakdown = Column(JSON, default={})  # Detailed risk breakdown
    pr_summary = Column(Text, nullable=True)  # Natural language PR summary for non-tech stakeholders

    project = relationship("Project", back_populates="runs")
    findings = relationship("Finding", back_populates="run", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("analysis_runs.id"), nullable=False, index=True)
    file_path = Column(String, nullable=False, index=True)
    line_number = Column(Integer, nullable=True)
    end_line_number = Column(Integer, nullable=True)
    severity = Column(SQLEnum(FindingSeverity), nullable=False, index=True)
    category = Column(SQLEnum(FindingCategory), nullable=False, index=True)
    rule_id = Column(String, nullable=True, index=True)  # e.g., "eslint:no-unused-vars", "AI:logic-error"
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    suggestion = Column(Text, nullable=True)
    code_snippet = Column(Text, nullable=True)
    is_ai_generated = Column(Integer, default=0, index=True)  # 0=rule-based, 1=AI
    is_resolved = Column(Integer, default=0, index=True)
    is_dismissed = Column(Integer, default=0, index=True)  # Learning system: user dismissed this finding
    auto_fix_code = Column(Text, nullable=True)  # AI-generated fix patch
    embedding = Column(ARRAY(Float), nullable=True)  # Phase 2: Semantic search vector (384-dim for all-MiniLM-L6-v2)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    finding_metadata = Column(JSON, default={})  # Additional context

    run = relationship("AnalysisRun", back_populates="findings")


# Phase 3A: Security & Verification Models

class EmailVerificationToken(Base):
    """Email verification tokens for new user registration."""
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)  # NULL if not used, timestamp if verified

    user = relationship("User", foreign_keys=[user_id])


class PasswordResetToken(Base):
    """Password reset tokens for forgot password flow."""
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)  # NULL if not used, timestamp if reset

    user = relationship("User", foreign_keys=[user_id])


class Subscription(Base):
    """Stripe subscription tracking for billing."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    
    # Subscription details
    tier = Column(String, nullable=False, index=True)  # FREE, PRO, ENTERPRISE
    status = Column(String, nullable=False, index=True)  # ACTIVE, TRIALING, PAST_DUE, CANCELED, etc.
    billing_interval = Column(String, nullable=True)  # MONTHLY, YEARLY (NULL for FREE)
    
    # Stripe integration
    stripe_subscription_id = Column(String, unique=True, nullable=True, index=True)
    stripe_price_id = Column(String, nullable=True)
    stripe_current_period_start = Column(DateTime, nullable=True)
    stripe_current_period_end = Column(DateTime, nullable=True)
    stripe_cancel_at_period_end = Column(Boolean, default=False)
    
    # Trial tracking
    trial_start = Column(DateTime, nullable=True)
    trial_end = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    canceled_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="subscription")


class UsageTracking(Base):
    """Track API usage per user per month for billing limits."""
    __tablename__ = "usage_tracking"
    __table_args__ = (
        UniqueConstraint('user_id', 'month', name='uq_user_month_usage'),
        Index('idx_usage_user_month', 'user_id', 'month'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Time period (e.g., "2024-01" for January 2024)
    month = Column(String, nullable=False, index=True)
    
    # Usage counters
    analyses_used = Column(Integer, default=0, nullable=False)
    analyses_limit = Column(Integer, nullable=False)  # Based on subscription tier
    
    # Additional metrics
    total_lines_analyzed = Column(Integer, default=0, nullable=False)
    total_findings_generated = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="usage_records")
