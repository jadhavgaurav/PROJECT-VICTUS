"""
OAuth handlers for Google and Microsoft
"""

import httpx
from typing import Dict
from sqlalchemy.orm import Session
from datetime import datetime

from ..models import User
from ..config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)

async def get_google_oauth_url() -> str:
    """Generate Google OAuth authorization URL."""
    from google_auth_oauthlib.flow import Flow
    
    redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://localhost:8000/api/auth/google/callback"
    
    # Create Flow with redirect_uri - must match exactly what's in Google Cloud Console
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        },
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
        redirect_uri=redirect_uri  # Explicitly set the redirect_uri for this flow
    )
    
    authorization_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    return authorization_url

async def handle_google_callback(code: str, db: Session) -> Dict:
    """Handle Google OAuth callback and create/update user."""
    from google_auth_oauthlib.flow import Flow
    
    redirect_uri = settings.GOOGLE_REDIRECT_URI or "http://localhost:8000/api/auth/google/callback"
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        },
        scopes=["openid", "https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
        redirect_uri=redirect_uri  # Explicitly set the redirect_uri for this flow
    )
    
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Get user info from Google
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {credentials.token}"}
        )
        user_info = response.json()
    
    # Find or create user
    user = db.query(User).filter(User.email == user_info["email"]).first()
    
    if user:
        # Update existing user
        if user.provider != "google":
            user.provider = "google"
        user.provider_id = user_info["id"]
        user.avatar_url = user_info.get("picture")
        user.last_login = datetime.utcnow()
        if not user.full_name:
            user.full_name = user_info.get("name")
    else:
        # Create new user
        user = User(
            email=user_info["email"],
            username=user_info["email"].split("@")[0],
            full_name=user_info.get("name"),
            provider="google",
            provider_id=user_info["id"],
            avatar_url=user_info.get("picture"),
            is_active=True,
            is_verified=user_info.get("verified_email", False),
            hashed_password=None
        )
        db.add(user)
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"Google OAuth user logged in: {user.email}")
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url
    }

async def get_microsoft_oauth_url() -> str:
    """Generate Microsoft OAuth authorization URL."""
    import msal
    
    redirect_uri = settings.MICROSOFT_REDIRECT_URI or "http://localhost:8000/api/auth/microsoft/callback"
    authority = f"https://login.microsoftonline.com/{settings.MS_TENANT_ID or 'common'}"
    
    # Web applications MUST use ConfidentialClientApplication with client secret
    if not settings.MS_CLIENT_SECRET:
        raise ValueError("MS_CLIENT_SECRET is required for Microsoft OAuth in web applications")
    
    app = msal.ConfidentialClientApplication(
        settings.MS_CLIENT_ID,
        client_credential=settings.MS_CLIENT_SECRET,
        authority=authority
    )
    
    # Request scopes needed for both login and M365 tools
    auth_url = app.get_authorization_request_url(
        scopes=["User.Read", "Mail.ReadWrite", "Mail.Send", "Calendars.ReadWrite"],
        redirect_uri=redirect_uri
    )
    
    return auth_url

async def handle_microsoft_callback(code: str, db: Session) -> Dict:
    """Handle Microsoft OAuth callback and create/update user."""
    import msal
    
    redirect_uri = settings.MICROSOFT_REDIRECT_URI or "http://localhost:8000/api/auth/microsoft/callback"
    authority = f"https://login.microsoftonline.com/{settings.MS_TENANT_ID or 'common'}"
    
    # Web applications MUST use ConfidentialClientApplication with client secret
    if not settings.MS_CLIENT_SECRET:
        raise ValueError("MS_CLIENT_SECRET is required for Microsoft OAuth in web applications")
    
    app = msal.ConfidentialClientApplication(
        settings.MS_CLIENT_ID,
        client_credential=settings.MS_CLIENT_SECRET,
        authority=authority
    )
    
    # Request scopes needed for both login and M365 tools
    result = app.acquire_token_by_authorization_code(
        code,
        scopes=["User.Read", "Mail.ReadWrite", "Mail.Send", "Calendars.ReadWrite"],
        redirect_uri=redirect_uri
    )
    
    if "error" in result:
        error_desc = result.get('error_description', result.get('error', 'Unknown error'))
        raise Exception(f"Microsoft OAuth error: {error_desc}")
    
    access_token = result["access_token"]
    refresh_token = result.get("refresh_token")
    expires_in = result.get("expires_in", 3600)  # Default to 1 hour
    
    # Calculate expiration time
    from datetime import timedelta
    token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    # Get user info from Microsoft Graph
    async with httpx.AsyncClient() as client:
        # Get user profile
        response = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        user_info = response.json()
        
        # Get organization/tenant info
        org_info = None
        try:
            org_response = await client.get(
                "https://graph.microsoft.com/v1.0/me/organization",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            if org_response.status_code == 200:
                orgs = org_response.json().get("value", [])
                if orgs:
                    org_info = orgs[0]  # Get first organization
        except Exception as e:
            logger.warning(f"Could not fetch organization info: {e}")
        
        # Get tenant info from user's domain
        user_domain = None
        email = user_info.get("mail") or user_info.get("userPrincipalName")
        if email and "@" in email:
            user_domain = email.split("@")[1]
        
        # Add organization info to user_info
        if org_info:
            user_info["organization"] = org_info.get("displayName", user_domain)
            user_info["tenant_id"] = org_info.get("id")
        elif user_domain:
            user_info["organization"] = user_domain
            user_info["tenant_id"] = None
    
    # Find or create user
    email = user_info.get("mail") or user_info.get("userPrincipalName")
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Update existing user
        if user.provider != "microsoft":
            user.provider = "microsoft"
        user.provider_id = user_info.get("id")
        user.avatar_url = None  # Microsoft Graph doesn't provide avatar in basic profile
        user.last_login = datetime.utcnow()
        if not user.full_name:
            user.full_name = user_info.get("displayName")
    else:
        # Create new user
        username = email.split("@")[0] if email else user_info.get("displayName", "user")
        user = User(
            email=email,
            username=username,
            full_name=user_info.get("displayName"),
            provider="microsoft",
            provider_id=user_info.get("id"),
            is_active=True,
            is_verified=True,
            hashed_password=None
        )
        db.add(user)
    
    # Store Microsoft tokens for M365 tools
    user.microsoft_access_token = access_token
    if refresh_token:
        user.microsoft_refresh_token = refresh_token
    user.microsoft_token_expires_at = token_expires_at
    
    db.commit()
    db.refresh(user)
    
    logger.info(f"Microsoft OAuth user logged in: {user.email}")
    
    # Determine account type
    account_type = "Personal"
    organization = user_info.get("organization", "")
    if organization and not any(x in organization.lower() for x in ["outlook", "hotmail", "live", "msn"]):
        account_type = "Work/School"
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "avatar_url": user.avatar_url,
        "organization": organization,
        "account_type": account_type,
        "tenant_id": user_info.get("tenant_id")
    }

