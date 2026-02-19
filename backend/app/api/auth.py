"""
Authentication API endpoints.

Provides signup, login, and user profile (me) endpoints using JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User
from app.services.auth_service import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

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
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── Endpoints ──────────────────────────────────────────────────────────────

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
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
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id), "email": user.email})

    return AuthResponse(
        access_token=token,
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


class ApiKeysResponse(BaseModel):
    has_groq_key: bool
    has_openai_key: bool
    has_anthropic_key: bool
    has_google_key: bool
    preferred_llm_provider: str


@router.get("/api-keys", response_model=ApiKeysResponse)
def get_api_keys(current_user: User = Depends(get_current_user)):
    """Get which API keys the user has configured (never returns actual keys)."""
    return ApiKeysResponse(
        has_groq_key=bool(current_user.groq_api_key),
        has_openai_key=bool(current_user.openai_api_key),
        has_anthropic_key=bool(current_user.anthropic_api_key),
        has_google_key=bool(current_user.google_api_key),
        preferred_llm_provider=current_user.preferred_llm_provider or "groq",
    )


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
    db.commit()
    db.refresh(current_user)
    return ApiKeysResponse(
        has_groq_key=bool(current_user.groq_api_key),
        has_openai_key=bool(current_user.openai_api_key),
        has_anthropic_key=bool(current_user.anthropic_api_key),
        has_google_key=bool(current_user.google_api_key),
        preferred_llm_provider=current_user.preferred_llm_provider or "groq",
    )
