"""
Authentication routes (signup, login, OAuth)
"""

import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from ..database import get_db
from ..models import User, Session as UserSession
from ..config import settings
from .security import verify_password, get_password_hash, generate_session_token, generate_csrf_token
from .dependencies import get_current_user, get_optional_user
from .dependencies import get_current_user, get_optional_user
from .oauth import OAuthService
from .oauth import OAuthService
from ..services.email import EmailService
from ..models import PasswordResetToken
from ..utils.logging import get_logger
import uuid
import secrets

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

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class OAuthFinalizeRequest(BaseModel):
    token: str
    username: str

class AuthResponse(BaseModel):
    user: dict

def set_auth_cookies(response: Response, session_token: str, csrf_token: str):
    """Helper to set authentication cookies."""
    # Session Cookie (HttpOnly, Secure in Prod)
    response.set_cookie(
        key="victus_session",
        value=session_token,
        httponly=True,
        samesite="lax",
        secure=False, # Set to True in Production (settings.IS_PROD)
        max_age=60 * 60 * 24 * 7, # 7 days
        path="/"
    )
    
    # CSRF Token (Not HttpOnly, readable by JS)
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        samesite="lax",
        secure=False, # Set to True in Production
        max_age=60 * 60 * 24 * 7,
        path="/"
    )

@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: UserSignup, response: Response, db: Session = Depends(get_db)):
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
        
        # Create Session
        session_token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(days=7)
        
        new_session = UserSession(
            id=session_token,
            user_id=new_user.id,
            expires_at=expires_at,
            user_agent="Signup",
            ip_address="0.0.0.0" # Should get from request
        )
        db.add(new_session)
        db.commit()
        
        # Set Cookies
        csrf_token = generate_csrf_token()
        set_auth_cookies(response, session_token, csrf_token)
        
        return AuthResponse(
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

@router.post("/login", response_model=AuthResponse)
async def login(credentials: UserLogin, response: Response, request: Request, db: Session = Depends(get_db)):
    """
    Authenticate user and set session cookie.
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
    
    # Create Session
    session_token = generate_session_token()
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    # Try to get IP and User Agent
    ip = request.client.host if request.client else "Unknown"
    ua = request.headers.get("user-agent", "Unknown")
    
    new_session = UserSession(
        id=session_token,
        user_id=user.id,
        expires_at=expires_at,
        user_agent=ua,
        ip_address=ip
    )
    db.add(new_session)
    db.commit()
    
    logger.info(f"User logged in: {user.email}")
    
    # Set Cookies
    csrf_token = generate_csrf_token()
    set_auth_cookies(response, session_token, csrf_token)
    
    return AuthResponse(
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
async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    """
    Logout user (revoke session).
    """
    session_id = request.cookies.get("victus_session")
    if session_id:
        session = db.query(UserSession).filter(UserSession.id == session_id).first()
        if session:
            session.revoked_at = datetime.utcnow()
            db.commit()
            
    response.delete_cookie("victus_session")
    response.delete_cookie("csrf_token")
    
    return {"message": "Successfully logged out"}

# OAuth Routes

@router.get("/oauth/{provider}/start")
async def oauth_start(provider: str, response: Response):
    """
    Start OAuth flow for Google or Microsoft.
    """
    state = OAuthService.generate_state()
    
    if provider == "google":
        auth_url = OAuthService.get_google_auth_url(state)
    elif provider == "microsoft":
        auth_url = OAuthService.get_microsoft_auth_url(state)
    else:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    # Store state in cookie to validate on callback (CSRF protection)
    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        samesite="lax",
        secure=False, # Set to True in Prod
        max_age=600 # 10 minutes
    )
    return response


@router.post("/oauth/finalize", response_model=AuthResponse)
async def finalize_oauth(
    request: OAuthFinalizeRequest, 
    response: Response, 
    http_request: Request,
    db: Session = Depends(get_db)
):
    """
    Finalize OAuth registration with a chosen username.
    """
    try:
        payload = jwt.decode(request.token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("email")
        provider = payload.get("provider")
        provider_id = payload.get("provider_id")
        name = payload.get("name")
        
        if not email or not provider or not provider_id:
             raise HTTPException(status_code=400, detail="Invalid token data")
             
        # Check if username taken
        if db.query(User).filter(User.username == request.username).first():
            raise HTTPException(status_code=400, detail="Username is already taken")
            
        # Create User
        import secrets
        random_pass = secrets.token_urlsafe(16)
        hashed = get_password_hash(random_pass)
        
        user = User(
            email=email,
            username=request.username,
            hashed_password=hashed,
            full_name=name,
            provider=provider,
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Link OAuth
        from ..models import OAuthAccount
        new_oauth = OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_id,
            email=email
        )
        db.add(new_oauth)
        db.commit()
        
        # Create Session
        session_token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(days=7)
        ip = http_request.client.host if http_request.client else "Unknown"
        ua = http_request.headers.get("user-agent", "Unknown")
        
        new_session = UserSession(
            id=session_token, 
            user_id=user.id, 
            expires_at=expires_at, 
            user_agent=ua, 
            ip_address=ip
        )
        db.add(new_session)
        db.commit()
        
        # Set Cookies
        csrf_token = generate_csrf_token()
        set_auth_cookies(response, session_token, csrf_token)
        
        return AuthResponse(
            user={
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url
            }
        )

    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired registration token")
    except Exception as e:
        logger.error(f"Finalize OAuth error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db),
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None
):
    """
    Handle OAuth callback, link account, and log in.
    """
    if error:
        redirect_url = f"{settings.FRONTEND_BASE_URL}/login?error=oauth_failed&details={error}"
        return RedirectResponse(url=redirect_url)
        
    if not code or not state:
        redirect_url = f"{settings.FRONTEND_BASE_URL}/login?error=invalid_callback"
        return RedirectResponse(url=redirect_url)
        
    # Validate state
    cookie_state = request.cookies.get("oauth_state")
    if not cookie_state or cookie_state != state:
         redirect_url = f"{settings.FRONTEND_BASE_URL}/login?error=invalid_state"
         return RedirectResponse(url=redirect_url)
         
    try:
        # Exchange code for user info
        user_info = {}
        tokens = {}
        
        if provider == "google":
            tokens, user_info = OAuthService.exchange_google_code(code)
            provider_uid = user_info.get("sub")
            email = user_info.get("email")
            name = user_info.get("name")
        elif provider == "microsoft":
            tokens, user_info = OAuthService.exchange_microsoft_code(code)
            provider_uid = user_info.get("id")
            email = user_info.get("userPrincipalName") or user_info.get("mail") # UPN is usually email
            name = user_info.get("displayName")
        else:
             raise HTTPException(status_code=400, detail="Invalid provider")
             
        if not email or not provider_uid:
             raise HTTPException(status_code=400, detail="Incomplete user info from provider")

        # 1. Check if OAuthAccount exists
        from ..models import OAuthAccount, OAuthProvider # Import here to avoid circulars if any
        
        oauth_account = db.query(OAuthAccount).filter(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_uid
        ).first()
        
        user = None
        
        if oauth_account:
            # Login existing user
            user = oauth_account.user
        else:
            # 2. Check if User exists with same email (Safe Linking Policy)
            existing_user = db.query(User).filter(User.email == email).first()
            
            if existing_user:
                # Link to existing user
                user = existing_user
                
                # Create OAuthAccount link
                new_oauth = OAuthAccount(
                    user_id=user.id,
                    provider=provider,
                    provider_user_id=provider_uid,
                    email=email
                )
                db.add(new_oauth)
                db.commit()
            else:
                # 3. New User -> Redirect to Completion Page
                registration_payload = {
                    "email": email,
                    "provider": provider,
                    "provider_id": provider_uid,
                    "name": name,
                    "exp": datetime.utcnow() + timedelta(minutes=15)
                }
                token = jwt.encode(registration_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
                
                redirect_url = f"{settings.FRONTEND_BASE_URL}/complete-oauth?token={token}&suggested={email.split('@')[0]}"
                return RedirectResponse(url=redirect_url)
            
        # 4. Create Session (Only for existing/linked users)
        session_token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(days=7)
        new_session = UserSession(id=session_token, user_id=user.id, expires_at=expires_at, user_agent="OAuth", ip_address=request.client.host if request.client else "Unknown")
        db.add(new_session)
        db.commit()
        
        # 5. Redirect with cookies
        redirect = RedirectResponse(url=f"{settings.FRONTEND_BASE_URL}/")
        
        # We must manually set cookies on the RedirectResponse object
        redirect.set_cookie(key="victus_session", value=session_token, httponly=True, samesite="lax", max_age=60*60*24*7)
        csrf = generate_csrf_token()
        redirect.set_cookie(key="csrf_token", value=csrf, httponly=False, samesite="lax", max_age=60*60*24*7)
        
        # Delete state cookie
        redirect.delete_cookie("oauth_state")
        
        return redirect

    except Exception as e:
        logger.error(f"OAuth Callback Error: {e}", exc_info=True)
        return RedirectResponse(f"{settings.FRONTEND_BASE_URL}/login?error=server_error")



@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Request a password reset email.
    """
    email = request.email.lower()
    user = db.query(User).filter(User.email == email).first()
    
    # Always return success to prevent user enumeration, 
    # unless in dev mode where we debug.
    if not user:
        # Simulate processing time
        return {"message": "If an account exists with this email, you will receive password reset instructions."}
    
    # Generate Token
    # We'll use a secure random string for the URL, and store it (or a hash) in DB.
    # For simplicity, we store the token as is in this implementation, 
    # but in high security it should be hashed like a password.
    raw_token = secrets.token_urlsafe(32)
    
    expires = datetime.utcnow() + timedelta(minutes=15)
    
    reset_token = PasswordResetToken(
        user_id=user.id,
        token=raw_token,
        expires_at=expires
    )
    db.add(reset_token)
    db.commit()
    
    # Send Email
    reset_link = f"{settings.FRONTEND_BASE_URL}/reset-password?token={raw_token}"
    
    await EmailService.send_email(
        recipients=[email],
        subject="Reset your password - PROJECT-VICTUS",
        template_name="reset_password.html",
        template_body={
            "link": reset_link,
            "year": datetime.utcnow().year
        }
    )
    
    return {"message": "If an account exists with this email, you will receive password reset instructions."}


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    Reset password using a valid token.
    """
    token = request.token
    
    # Find token
    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()
    
    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token"
        )
        
    # Get user
    user = db.query(User).filter(User.id == reset_record.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Update Password
    user.hashed_password = get_password_hash(request.new_password)
    
    # Mark token used
    reset_record.used = True
    
    # Optionally: Revoke all existing sessions for security
    # db.query(UserSession).filter(UserSession.user_id == user.id).delete()
    
    db.commit()
    
    return {"message": "Password has been reset successfully. You can now login."}


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change password for logged in user.
    """
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
        
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password updated successfully"}
