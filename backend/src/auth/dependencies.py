from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime

from ..database import get_db
from ..models import User, Session as UserSession
from ..utils.logging import get_logger

logger = get_logger(__name__)

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from session cookie.
    """
    session_id = request.cookies.get("victus_session")
    
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
        
    # Look up session
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )
        
    if session.expires_at < datetime.utcnow():
        # Clean up expired session?
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )
        
    if session.revoked_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session revoked",
        )
        
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    # CSRF Check for state-changing methods
    if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
        csrf_cookie = request.cookies.get("csrf_token")
        csrf_header = request.headers.get("X-CSRF-Token")
        
        # In dev, we might be lenient or strictly enforce.
        # Requirement: "backend validates match"
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            logger.warning(f"CSRF mismatch for user {user.id}. Cookie: {csrf_cookie}, Header: {csrf_header}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF validation failed"
            )
        
    return user

async def get_optional_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise return None.
    """
    try:
        return await get_current_user(request, db)
    except HTTPException:
        return None
