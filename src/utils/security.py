"""
Security utilities - Rate limiting, CORS, input validation
"""

from fastapi import Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import List
import re

from ..config import settings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

def setup_cors(app) -> None:
    """Setup CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def setup_rate_limiting(app) -> None:
    """Setup rate limiting."""
    if settings.RATE_LIMIT_ENABLED:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def validate_input(text: str, max_length: int = 10000) -> str:
    """
    Validate and sanitize user input.
    
    Args:
        text: Input text to validate
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
        
    Raises:
        HTTPException: If input is invalid
    """
    if not text or not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Input must be a non-empty string")
    
    if len(text) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"Input too long. Maximum length is {max_length} characters"
        )
    
    # Remove potentially dangerous characters (basic sanitization)
    # In production, use a proper sanitization library
    text = text.strip()
    
    # Check for SQL injection patterns (basic)
    sql_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|/\*|\*/)",
    ]
    for pattern in sql_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise HTTPException(
                status_code=400,
                detail="Invalid input detected"
            )
    
    return text

def validate_session_id(session_id: str) -> str:
    """Validate session ID format."""
    if not session_id or not isinstance(session_id, str):
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    # Session ID should be alphanumeric with dashes/underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        raise HTTPException(status_code=400, detail="Invalid session ID format")
    
    if len(session_id) > 100:
        raise HTTPException(status_code=400, detail="Session ID too long")
    
    return session_id

