"""
Email service for sending transactional emails with templates.
Phase 3A: Security & Legal - Email verification, password reset, notifications.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from jinja2 import Template

from app.config import settings

logger = logging.getLogger(__name__)


# Email Templates (using Jinja2)

EMAIL_VERIFICATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #4F46E5; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background: #f9fafb; }
        .button { display: inline-block; padding: 12px 24px; background: #4F46E5; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
        .code { font-family: monospace; font-size: 18px; background: #e5e7eb; padding: 10px; border-radius: 4px; letter-spacing: 2px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to AI Code Review!</h1>
        </div>
        <div class="content">
            <h2>Hi {{ name }},</h2>
            <p>Thank you for signing up! Please verify your email address to activate your account.</p>
            
            <p style="text-align: center;">
                <a href="{{ verification_url }}" class="button">Verify Email Address</a>
            </p>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #4F46E5;">{{ verification_url }}</p>
            
            <p><strong>This link expires in {{ expires_hours }} hours.</strong></p>
            
            <p>If you didn't create an account, you can safely ignore this email.</p>
        </div>
        <div class="footer">
            <p>&copy; {{ year }} AI Code Review. All rights reserved.</p>
            <p>This is an automated email. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
"""

PASSWORD_RESET_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #DC2626; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background: #f9fafb; }
        .button { display: inline-block; padding: 12px 24px; background: #DC2626; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
        .warning { background: #FEF3C7; padding: 15px; border-left: 4px solid #F59E0B; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Password Reset Request</h1>
        </div>
        <div class="content">
            <h2>Hi {{ name }},</h2>
            <p>We received a request to reset your password for your AI Code Review account.</p>
            
            <p style="text-align: center;">
                <a href="{{ reset_url }}" class="button">Reset Password</a>
            </p>
            
            <p>Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #DC2626;">{{ reset_url }}</p>
            
            <p><strong>This link expires in {{ expires_hours }} hour(s).</strong></p>
            
            <div class="warning">
                <strong>⚠️ Security Notice:</strong>
                <p>If you didn't request a password reset, please ignore this email and ensure your account is secure. Consider changing your password if you suspect unauthorized access.</p>
            </div>
        </div>
        <div class="footer">
            <p>&copy; {{ year }} AI Code Review. All rights reserved.</p>
            <p>This is an automated email. Please do not reply.</p>
        </div>
    </div>
</body>
</html>
"""

WELCOME_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #10B981; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background: #f9fafb; }
        .button { display: inline-block; padding: 12px 24px; background: #10B981; color: white; text-decoration: none; border-radius: 6px; margin: 10px 5px; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
        .feature { margin: 15px 0; padding: 15px; background: white; border-radius: 6px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Email Verified!</h1>
        </div>
        <div class="content">
            <h2>Welcome, {{ name }}!</h2>
            <p>Your email has been successfully verified. You're all set to start using AI Code Review.</p>
            
            <h3>🚀 Get Started:</h3>
            <div class="feature">
                <strong>1. Connect GitHub</strong>
                <p>Add your GitHub Personal Access Token to analyze your repositories.</p>
            </div>
            <div class="feature">
                <strong>2. Configure LLM</strong>
                <p>Add your API key for Groq, OpenAI, Anthropic, or Google AI.</p>
            </div>
            <div class="feature">
                <strong>3. Analyze Your First PR</strong>
                <p>Start analyzing pull requests with AI-powered insights!</p>
            </div>
            
            <p style="text-align: center;">
                <a href="{{ dashboard_url }}" class="button">Go to Dashboard</a>
                <a href="{{ docs_url }}" class="button" style="background: #6366F1;">Read Docs</a>
            </p>
        </div>
        <div class="footer">
            <p>&copy; {{ year }} AI Code Review. All rights reserved.</p>
            <p>Need help? Contact us or check our documentation.</p>
        </div>
    </div>
</body>
</html>
"""

NOTIFICATION_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #6366F1; color: white; padding: 20px; text-align: center; }
        .content { padding: 30px; background: #f9fafb; }
        .button { display: inline-block; padding: 12px 24px; background: #6366F1; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }
        .footer { text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ subject }}</h1>
        </div>
        <div class="content">
            {{ content }}
        </div>
        <div class="footer">
            <p>&copy; {{ year }} AI Code Review. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""


class EmailService:
    """Service for sending emails with templates."""
    
    def __init__(self):
        self.enabled = settings.enable_email
        if not self.enabled:
            logger.info("Email service is disabled. Set ENABLE_EMAIL=true to enable.")
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """Send an email using SMTP."""
        if not self.enabled:
            logger.info(f"Email disabled. Would have sent to {to_email}: {subject}")
            return True  # Graceful degradation
        
        if not settings.smtp_username or not settings.smtp_password:
            logger.warning("SMTP credentials not configured. Skipping email send.")
            return False
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{from_name or settings.smtp_from_name} <{from_email or settings.smtp_from_email}>"
            message["To"] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send via SMTP
            async with aiosmtplib.SMTP(
                hostname=settings.smtp_host,
                port=settings.smtp_port,
                use_tls=False,  # We'll use STARTTLS
            ) as smtp:
                await smtp.connect()
                await smtp.starttls()
                await smtp.login(settings.smtp_username, settings.smtp_password)
                await smtp.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    async def send_verification_email(
        self,
        to_email: str,
        name: str,
        verification_token: str
    ) -> bool:
        """Send email verification email."""
        verification_url = f"{settings.frontend_url}/verify-email?token={verification_token}"
        
        template = Template(EMAIL_VERIFICATION_TEMPLATE)
        html_content = template.render(
            name=name,
            verification_url=verification_url,
            expires_hours=settings.email_verification_token_expire_hours,
            year=datetime.utcnow().year
        )
        
        return await self.send_email(
            to_email=to_email,
            subject="Verify Your Email - AI Code Review",
            html_content=html_content
        )
    
    async def send_password_reset_email(
        self,
        to_email: str,
        name: str,
        reset_token: str
    ) -> bool:
        """Send password reset email."""
        reset_url = f"{settings.frontend_url}/reset-password?token={reset_token}"
        
        template = Template(PASSWORD_RESET_TEMPLATE)
        html_content = template.render(
            name=name,
            reset_url=reset_url,
            expires_hours=settings.password_reset_token_expire_hours,
            year=datetime.utcnow().year
        )
        
        return await self.send_email(
            to_email=to_email,
            subject="Password Reset Request - AI Code Review",
            html_content=html_content
        )
    
    async def send_welcome_email(
        self,
        to_email: str,
        name: str
    ) -> bool:
        """Send welcome email after verification."""
        template = Template(WELCOME_EMAIL_TEMPLATE)
        html_content = template.render(
            name=name,
            dashboard_url=f"{settings.frontend_url}/dashboard",
            docs_url=f"{settings.frontend_url}/docs",
            year=datetime.utcnow().year
        )
        
        return await self.send_email(
            to_email=to_email,
            subject="Welcome to AI Code Review! 🎉",
            html_content=html_content
        )
    
    async def send_notification_email(
        self,
        to_email: str,
        subject: str,
        content: str
    ) -> bool:
        """Send a general notification email."""
        template = Template(NOTIFICATION_TEMPLATE)
        html_content = template.render(
            subject=subject,
            content=content,
            year=datetime.utcnow().year
        )
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get the singleton email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
