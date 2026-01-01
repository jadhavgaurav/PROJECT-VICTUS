"""
Authentication routes (signup, login, OAuth)
"""

import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..config import settings
from .jwt import verify_password, get_password_hash, create_access_token
from .dependencies import get_current_user
from .oauth import get_google_oauth_url, handle_google_callback, get_microsoft_oauth_url, handle_microsoft_callback
from ..utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Pydantic models
class UserSignup(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """
    Create a new user account.
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or username already registered"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            provider="local",
            is_active=True,
            is_verified=False
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {user_data.email}")
        
        # Create access token (sub must be a string for JWT)
        access_token = create_access_token(data={"sub": str(new_user.id)})
        
        return TokenResponse(
            access_token=access_token,
            user={
                "id": new_user.id,
                "email": new_user.email,
                "username": new_user.username,
                "full_name": new_user.full_name,
                "avatar_url": new_user.avatar_url
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating account: {str(e)}"
        )

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.
    """
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    logger.info(f"User logged in: {user.email}")
    
    # Create access token (sub must be a string for JWT)
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user={
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url
        }
    )

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    """
    user_info = {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "avatar_url": current_user.avatar_url,
        "provider": current_user.provider,
        "is_verified": current_user.is_verified
    }
    
    # For Microsoft users, try to get organization info from email domain
    if current_user.provider == "microsoft" and current_user.email:
        email_domain = current_user.email.split("@")[1] if "@" in current_user.email else ""
        if email_domain:
            # Determine account type from domain
            if any(x in email_domain.lower() for x in ["outlook", "hotmail", "live", "msn"]):
                user_info["account_type"] = "Personal"
                user_info["organization"] = "Microsoft Account"
            else:
                user_info["account_type"] = "Work/School"
                user_info["organization"] = email_domain
    
    return user_info

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout user (client should discard token).
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}

# OAuth Routes
@router.get("/google/login")
async def google_login():
    """
    Initiate Google OAuth login.
    """
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not configured"
        )
    
    try:
        auth_url = await get_google_oauth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth not available. Please use email/password."
        )

@router.get("/google/callback")
async def google_callback(
    code: Optional[str] = None,
    error: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Handle Google OAuth callback.
    """
    if error:
        logger.error(f"Google OAuth error: {error}")
        return RedirectResponse(url="/login?error=oauth_failed")
    
    if not code:
        return RedirectResponse(url="/login?error=no_code")
    
    try:
        user_data = await handle_google_callback(code, db)
        access_token = create_access_token(data={"sub": str(user_data["id"])})
        
        # Redirect to frontend with token
        redirect_url = f"/?token={access_token}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Google OAuth error: {e}")
        return RedirectResponse(url="/login?error=oauth_failed")

@router.get("/microsoft/login")
async def microsoft_login():
    """
    Initiate Microsoft OAuth login.
    """
    if not settings.MS_CLIENT_ID or not settings.MS_TENANT_ID:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Microsoft OAuth not configured"
        )
    
    # Client secret is REQUIRED for web applications
    if not settings.MS_CLIENT_SECRET:
        logger.error("MS_CLIENT_SECRET is required for Microsoft OAuth in web applications")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Microsoft OAuth is not configured. Please use email/password or Google OAuth to login."
        )
    
    try:
        auth_url = await get_microsoft_oauth_url()
        return {"auth_url": auth_url}
    except Exception as e:
        logger.error(f"Microsoft OAuth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Microsoft OAuth not available. Please use email/password."
        )

@router.get("/microsoft/callback")
async def microsoft_callback(
    code: Optional[str] = None,
    error: Optional[str] = None,
    request: Request = None,
    db: Session = Depends(get_db)
):
    """
    Handle Microsoft OAuth callback.
    """
    if error:
        logger.error(f"Microsoft OAuth error: {error}")
        return RedirectResponse(url="/login?error=oauth_failed")
    
    if not code:
        return RedirectResponse(url="/login?error=no_code")
    
    try:
        user_data = await handle_microsoft_callback(code, db)
        access_token = create_access_token(data={"sub": str(user_data["id"])})
        
        # Redirect to frontend with token
        redirect_url = f"/?token={access_token}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Microsoft OAuth error: {e}")
        return RedirectResponse(url="/login?error=oauth_failed")

