"""
Microsoft 365 authentication using MSAL
"""

import os
import msal
import atexit
from typing import Optional
from datetime import datetime, timezone

from .config import settings
from .utils.logging import get_logger
from .utils.context import get_session_id

logger = get_logger(__name__)

CLIENT_ID = settings.MS_CLIENT_ID
TENANT_ID = settings.MS_TENANT_ID
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}" if TENANT_ID else None
SCOPES = ["User.Read", "Mail.ReadWrite", "Mail.Send", "Calendars.ReadWrite"]

# Persist token cache
CACHE_FILE = ".msal_token_cache.json"

def save_cache(cache):
    """Save token cache to file."""
    if cache.has_state_changed:
        try:
            with open(CACHE_FILE, "w") as f:
                f.write(cache.serialize())
        except Exception as e:
            logger.error(f"Error saving token cache: {e}")

def load_cache():
    """Load token cache from file."""
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                cache.deserialize(f.read())
        except Exception as e:
            logger.warning(f"Error loading token cache: {e}")
    atexit.register(lambda: save_cache(cache))
    return cache

token_cache = load_cache()

if CLIENT_ID and TENANT_ID:
    app = msal.PublicClientApplication(
        CLIENT_ID, authority=AUTHORITY, token_cache=token_cache
    )
else:
    app = None
    logger.warning("Microsoft 365 credentials not configured. M365 tools will not work.")

def get_access_token() -> Optional[str]:
    """
    Acquires an access token for Microsoft Graph API.
    First tries to use stored token from user's OAuth session, then falls back to device flow.
    """
    # Try to get token from user's OAuth session (preferred method)
    try:
        session_id = get_session_id()
        if session_id:
            # session_id is set to user.id for authenticated users
            try:
                user_id = int(session_id)
                from .database import SessionLocal
                from .models import User
                
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user and user.provider == "microsoft" and user.microsoft_access_token:
                        # Check if token is expired
                        if user.microsoft_token_expires_at:
                            expires_at = user.microsoft_token_expires_at
                            if isinstance(expires_at, datetime):
                                # Add 5 minute buffer for expiration check
                                if expires_at > datetime.now(expires_at.tzinfo):
                                    logger.info(f"Using stored Microsoft token for user {user.email}")
                                    return user.microsoft_access_token
                                else:
                                    logger.info(f"Stored token expired, attempting refresh for user {user.email}")
                                    # Token expired, try to refresh
                                    if user.microsoft_refresh_token and settings.MS_CLIENT_SECRET:
                                        refreshed_token = _refresh_token(user.microsoft_refresh_token, user, db)
                                        if refreshed_token:
                                            return refreshed_token
                        else:
                            # No expiration info, assume valid
                            logger.info(f"Using stored Microsoft token (no expiration) for user {user.email}")
                            return user.microsoft_access_token
                finally:
                    db.close()
            except (ValueError, TypeError):
                # session_id is not a user ID, continue to fallback
                pass
    except Exception as e:
        logger.warning(f"Error getting token from user session: {e}")
    
    # Fallback to device flow (for backward compatibility or non-OAuth users)
    if not app:
        logger.error("MSAL app not initialized. Check MS_CLIENT_ID and MS_TENANT_ID.")
        return None
    
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result:
            save_cache(token_cache)
            return result.get("access_token")

    # Last resort: device flow
    try:
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            logger.error("Failed to create device flow. Check your app registration.")
            return None

        logger.info(f"MSAL: {flow['message']}")
        logger.warning("Using device code flow. For better experience, login with Microsoft OAuth.")
        result = app.acquire_token_by_device_flow(flow)

        if "access_token" in result:
            save_cache(token_cache)
            return result.get("access_token")
        else:
            logger.error(f"Authentication failed: {result.get('error')}")
            logger.error(f"Description: {result.get('error_description')}")
            logger.error(f"Correlation ID: {result.get('correlation_id')}")
            return None
    except Exception as e:
        logger.error(f"Error during authentication: {e}")
        return None

def _refresh_token(refresh_token: str, user, db) -> Optional[str]:
    """Refresh an expired Microsoft access token."""
    try:
        import msal
        authority = f"https://login.microsoftonline.com/{settings.MS_TENANT_ID or 'common'}"
        app = msal.ConfidentialClientApplication(
            settings.MS_CLIENT_ID,
            client_credential=settings.MS_CLIENT_SECRET,
            authority=authority
        )
        
        result = app.acquire_token_by_refresh_token(refresh_token, SCOPES)
        
        if "access_token" in result:
            from datetime import timedelta
            access_token = result["access_token"]
            new_refresh_token = result.get("refresh_token", refresh_token)
            expires_in = result.get("expires_in", 3600)
            token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Update user's tokens
            user.microsoft_access_token = access_token
            user.microsoft_refresh_token = new_refresh_token
            user.microsoft_token_expires_at = token_expires_at
            db.commit()
            
            logger.info(f"Successfully refreshed Microsoft token for user {user.email}")
            return access_token
        else:
            logger.error(f"Token refresh failed: {result.get('error')}")
            return None
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return None

def is_authenticated() -> bool:
    """Check if we have a cached token without prompting for login."""
    if not app:
        return False
    return bool(app.get_accounts())

