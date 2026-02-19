"""
Authentication API endpoints.

Provides signup, login, and user profile (me) endpoints using JWT tokens.
Phase 3A: Email verification, password reset, and GDPR compliance.
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets
import logging

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, EmailVerificationToken, PasswordResetToken, Project, AnalysisRun, Finding
from app.services.auth_service import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from app.services.email_service import get_email_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Request / Response schemas ─────────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    is_active: bool
    email_verified: bool = False  # Phase 3A: Email verification status
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Register a new user account and send verification email."""
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        name=body.name,
        email=body.email,
        hashed_password=get_password_hash(body.password),
        email_verified=False,  # Phase 3A: Require email verification
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate verification token
    token = secrets.token_urlsafe(32)
    verification_token = EmailVerificationToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=settings.email_verification_token_expire_hours)
    )
    db.add(verification_token)
    db.commit()

    # Send verification email in background
    email_service = get_email_service()
    background_tasks.add_task(
        email_service.send_verification_email,
        to_email=user.email,
        name=user.name,
        verification_token=token
    )

    # Return JWT token (user can use app but some features require verification)
    jwt_token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return AuthResponse(
        access_token=jwt_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and return a JWT token."""
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return UserResponse.model_validate(current_user)


# ── API Key Management (SaaS) ──────────────────────────────────────────────

class ApiKeysRequest(BaseModel):
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    preferred_llm_provider: Optional[str] = None
    github_token: Optional[str] = None


class ApiKeysResponse(BaseModel):
    has_groq_key: bool
    has_openai_key: bool
    has_anthropic_key: bool
    has_google_key: bool
    preferred_llm_provider: str
    has_github_token: bool
    github_username: Optional[str] = None


@router.get("/api-keys", response_model=ApiKeysResponse)
def get_api_keys(current_user: User = Depends(get_current_user)):
    """Get which API keys the user has configured (never returns actual keys)."""
    github_username = None
    if current_user.github_token:
        try:
            from app.services.github_pat_service import GitHubPATService
            gh = GitHubPATService(current_user.github_token)
            info = gh.validate_token()
            if info.get("valid"):
                github_username = info.get("login")
        except Exception:
            pass

    return ApiKeysResponse(
        has_groq_key=bool(current_user.groq_api_key),
        has_openai_key=bool(current_user.openai_api_key),
        has_anthropic_key=bool(current_user.anthropic_api_key),
        has_google_key=bool(current_user.google_api_key),
        preferred_llm_provider=current_user.preferred_llm_provider or "groq",
        has_github_token=bool(current_user.github_token),
        github_username=github_username,
    )


@router.post("/test-github-token")
def test_github_token(
    current_user: User = Depends(get_current_user),
):
    """Test the user's stored GitHub token and return account info."""
    if not current_user.github_token:
        raise HTTPException(status_code=400, detail="No GitHub token configured")

    from app.services.github_pat_service import GitHubPATService
    gh = GitHubPATService(current_user.github_token)
    result = gh.validate_token()
    if not result.get("valid"):
        raise HTTPException(status_code=401, detail=result.get("error", "Invalid token"))
    return result


@router.get("/webhook-info")
def get_webhook_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get webhook URL and secret for setting up GitHub webhooks."""
    from app.services.github_pat_service import generate_webhook_secret
    
    # Generate webhook secret if not exists
    if not current_user.github_webhook_secret:
        current_user.github_webhook_secret = generate_webhook_secret()
        db.commit()
        db.refresh(current_user)
    
    # Construct webhook URL (will need to be adjusted for production)
    base_url = settings.frontend_url.replace("http://localhost:5173", "http://localhost:8000")
    if settings.is_production:
        # In production, this should be the public API URL
        base_url = settings.frontend_url.replace("https://", "https://api.")
    
    webhook_url = f"{base_url}/api/webhooks/github/{current_user.id}"
    
    return {
        "webhook_url": webhook_url,
        "webhook_secret": current_user.github_webhook_secret,
        "user_id": current_user.id,
        "instructions": "Create a webhook on your GitHub repo with the URL above and the secret. Select 'Pull requests' events.",
    }

@router.put("/api-keys", response_model=ApiKeysResponse)
def update_api_keys(
    body: ApiKeysRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update user's LLM API keys. Send empty string to clear a key."""
    if body.groq_api_key is not None:
        current_user.groq_api_key = body.groq_api_key or None
    if body.openai_api_key is not None:
        current_user.openai_api_key = body.openai_api_key or None
    if body.anthropic_api_key is not None:
        current_user.anthropic_api_key = body.anthropic_api_key or None
    if body.google_api_key is not None:
        current_user.google_api_key = body.google_api_key or None
    if body.preferred_llm_provider is not None:
        current_user.preferred_llm_provider = body.preferred_llm_provider
    if body.github_token is not None:
        current_user.github_token = body.github_token or None
        # Generate a webhook secret for this user if they don't have one
        if current_user.github_token and not current_user.github_webhook_secret:
            from app.services.github_pat_service import generate_webhook_secret
            current_user.github_webhook_secret = generate_webhook_secret()
    db.commit()
    db.refresh(current_user)

    github_username = None
    if current_user.github_token:
        try:
            from app.services.github_pat_service import GitHubPATService
            gh = GitHubPATService(current_user.github_token)
            info = gh.validate_token()
            if info.get("valid"):
                github_username = info.get("login")
        except Exception:
            pass

    return ApiKeysResponse(
        has_groq_key=bool(current_user.groq_api_key),
        has_openai_key=bool(current_user.openai_api_key),
        has_anthropic_key=bool(current_user.anthropic_api_key),
        has_google_key=bool(current_user.google_api_key),
        preferred_llm_provider=current_user.preferred_llm_provider or "groq",
        has_github_token=bool(current_user.github_token),
        github_username=github_username,
    )
