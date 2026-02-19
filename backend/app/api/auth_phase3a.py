"""
Phase 3A Security Extensions for Authentication API.

Email verification, password reset, and GDPR compliance endpoints.
These should be merged into auth.py or imported separately.
"""

from datetime import datetime, timedelta
import secrets
import logging

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, EmailVerificationToken, PasswordResetToken, Project, AnalysisRun, Finding
from app.services.auth_service import get_current_user, get_password_hash, verify_password
from app.services.email_service import get_email_service

logger = logging.getLogger(__name__)

router = APIRouter()


# ── Phase 3A: Email Verification ──────────────────────────────────────────

class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


@router.post("/verify-email")
async def verify_email(
    body: VerifyEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Verify user's email address using the token from email."""
    verification = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == body.token
    ).first()
    
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    # Check if already used
    if verification.used_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification link has already been used"
        )
    
    # Check if expired
    if datetime.utcnow() > verification.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification link has expired. Please request a new one"
        )
    
    # Update user and mark token as used
    user = db.query(User).filter(User.id == verification.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.email_verified = True
    verification.used_at = datetime.utcnow()
    db.commit()
    
    # Send welcome email in background
    email_service = get_email_service()
    background_tasks.add_task(
        email_service.send_welcome_email,
        to_email=user.email,
        name=user.name
    )
    
    return {"message": "Email verified successfully!", "email_verified": True}


@router.post("/resend-verification")
async def resend_verification_email(
    body: ResendVerificationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Resend verification email to user."""
    user = db.query(User).filter(User.email == body.email).first()
    
    if not user:
        # Don't reveal if email exists or not (security best practice)
        return {"message": "If the email exists, a verification link has been sent"}
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Invalidate old tokens (mark as used)
    old_tokens = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user.id,
        EmailVerificationToken.used_at.is_(None)
    ).all()
    for token in old_tokens:
        token.used_at = datetime.utcnow()
    
    # Generate new token
    token = secrets.token_urlsafe(32)
    verification_token = EmailVerificationToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=settings.email_verification_token_expire_hours)
    )
    db.add(verification_token)
    db.commit()
    
    # Send email in background
    email_service = get_email_service()
    background_tasks.add_task(
        email_service.send_verification_email,
        to_email=user.email,
        name=user.name,
        verification_token=token
    )
    
    return {"message": "Verification email has been sent"}


# ── Phase 3A: Password Reset ──────────────────────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, max_length=128)


@router.post("/forgot-password")
async def forgot_password(
    body: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Send password reset email to user."""
    user = db.query(User).filter(User.email == body.email).first()
    
    # Don't reveal if email exists or not (security best practice)
    if not user:
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Invalidate old tokens
    old_tokens = db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.used_at.is_(None)
    ).all()
    for token in old_tokens:
        token.used_at = datetime.utcnow()
    
    # Generate new token
    token = secrets.token_urlsafe(32)
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=settings.password_reset_token_expire_hours)
    )
    db.add(reset_token)
    db.commit()
    
    # Send email in background
    email_service = get_email_service()
    background_tasks.add_task(
        email_service.send_password_reset_email,
        to_email=user.email,
        name=user.name,
        reset_token=token
    )
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
def reset_password(
    body: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset user's password using the token from email."""
    reset = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == body.token
    ).first()
    
    if not reset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if already used
    if reset.used_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reset link has already been used"
        )
    
    # Check if expired
    if datetime.utcnow() > reset.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset link has expired. Please request a new one"
        )
    
    # Update password and mark token as used
    user = db.query(User).filter(User.id == reset.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hashed_password = get_password_hash(body.new_password)
    reset.used_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password reset successfully"}


# ── Phase 3A: GDPR Compliance ─────────────────────────────────────────────

@router.get("/gdpr/export-data")
def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user data (GDPR Article 15 - Right to Access)."""
    # Gather all user data
    projects = db.query(Project).filter(Project.owner_id == current_user.id).all()
    
    projects_data = []
    for project in projects:
        runs = db.query(AnalysisRun).filter(AnalysisRun.project_id == project.id).all()
        runs_data = []
        for run in runs:
            findings = db.query(Finding).filter(Finding.run_id == run.id).all()
            runs_data.append({
                "id": run.id,
                "pr_number": run.pr_number,
                "pr_url": run.pr_url,
                "pr_title": run.pr_title,
                "status": run.status.value,
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "completed_at": run.completed_at.isoformat() if run.completed_at else None,
                "risk_score": run.risk_score,
                "findings_count": len(findings),
                "findings": [
                    {
                        "severity": f.severity.value,
                        "category": f.category.value,
                        "title": f.title,
                        "description": f.description,
                        "file_path": f.file_path,
                        "line_number": f.line_number,
                    }
                    for f in findings
                ]
            })
        
        projects_data.append({
            "id": project.id,
            "name": project.name,
            "github_repo": project.github_repo_full_name,
            "created_at": project.created_at.isoformat() if project.created_at else None,
            "analysis_runs": runs_data
        })
    
    user_data = {
        "user_profile": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "email_verified": current_user.email_verified,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        },
        "api_keys_configured": {
            "has_groq_key": bool(current_user.groq_api_key),
            "has_openai_key": bool(current_user.openai_api_key),
            "has_anthropic_key": bool(current_user.anthropic_api_key),
            "has_google_key": bool(current_user.google_api_key),
            "has_github_token": bool(current_user.github_token),
            "preferred_llm_provider": current_user.preferred_llm_provider,
        },
        "projects": projects_data,
        "export_metadata": {
            "export_date": datetime.utcnow().isoformat(),
            "data_format_version": "1.0",
            "gdpr_article": "Article 15 - Right to Access",
        }
    }
    
    return user_data


class DeleteAccountRequest(BaseModel):
    password: str = Field(..., description="Confirm password to delete account")
    confirmation: str = Field(..., description="Type 'DELETE' to confirm")


@router.delete("/gdpr/delete-account")
def delete_user_account(
    body: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete user account and all associated data (GDPR Article 17 - Right to Erasure)."""
    # Verify password
    if not verify_password(body.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Verify confirmation
    if body.confirmation != "DELETE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Confirmation must be 'DELETE'"
        )
    
    # Delete all user data (cascading will handle related records)
    # 1. Projects (and their runs/findings via cascade)
    db.query(Project).filter(Project.owner_id == current_user.id).delete()
    
    # 2. Verification tokens
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == current_user.id
    ).delete()
    
    # 3. Password reset tokens
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == current_user.id
    ).delete()
    
    # 4. Finally, delete the user
    db.delete(current_user)
    db.commit()
    
    logger.info(f"User account deleted: {current_user.email} (ID: {current_user.id}) - GDPR Article 17")
    
    return {
        "message": "Account successfully deleted",
        "email": current_user.email,
        "deleted_at": datetime.utcnow().isoformat(),
        "gdpr_article": "Article 17 - Right to Erasure"
    }
