from passlib.context import CryptContext
from datetime import datetime, timedelta
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def generate_session_token() -> str:
    """Generate a secure random session token."""
    return secrets.token_urlsafe(32)

def generate_csrf_token() -> str:
    """Generate a secure random CSRF token."""
    return secrets.token_hex(32)
