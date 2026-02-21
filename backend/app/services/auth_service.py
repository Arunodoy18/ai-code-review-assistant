"""
Authentication service.

Handles password hashing, JWT creation/verification, and the ``get_current_user``
FastAPI dependency for protecting routes.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

try:
    from jose import JWTError, jwt
except ImportError as _exc:
    raise ImportError(
        "python-jose is required for authentication. "
        "Install it with: pip install python-jose[cryptography]"
    ) from _exc

try:
    import bcrypt
except ImportError as _exc:
    raise ImportError(
        "bcrypt is required for password hashing. "
        "Install it with: pip install bcrypt"
    ) from _exc

from app.config import settings
from app.database import get_db

# ── Password hashing ──────────────────────────────────────────────────────


def _truncate_password(password: str, max_bytes: int = 72) -> bytes:
    """Truncate password to fit bcrypt's 72-byte limit while preserving UTF-8 integrity."""
    encoded = password.encode('utf-8')
    if len(encoded) <= max_bytes:
        return encoded
    
    # Truncate character by character until we fit
    for i in range(len(password), 0, -1):
        truncated = password[:i].encode('utf-8')
        if len(truncated) <= max_bytes:
            return truncated
    
    return password[:1].encode('utf-8')  # Fallback: at least 1 character


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    safe_password = _truncate_password(plain_password)
    return bcrypt.checkpw(safe_password, hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    safe_password = _truncate_password(password)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(safe_password, salt)
    return hashed.decode('utf-8')


# ── JWT tokens ─────────────────────────────────────────────────────────────

ALGORITHM = settings.jwt_algorithm
SECRET_KEY = settings.jwt_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT.  Raises JWTError on failure."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


# ── FastAPI dependency ─────────────────────────────────────────────────────

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """Return the authenticated User or raise 401.

    Reads the ``Authorization: Bearer <token>`` header.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from app.models import User  # local import to avoid circular dependency

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated")

    return user


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    """Return the authenticated User or ``None`` (no error).

    Useful for endpoints that work for both anonymous and authenticated users.
    """
    if credentials is None:
        return None
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None
