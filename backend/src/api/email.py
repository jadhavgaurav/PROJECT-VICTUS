"""
Email integration endpoints (Microsoft 365)
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import requests

from ..database import get_db
from ..models import User
from ..auth.dependencies import get_optional_user
from ..m365_auth import get_access_token
from ..utils.logging import get_logger
from ..utils.context import set_session_id
from .schemas import EmailsResponse, EmailItem, UnreadCountResponse, M365StatusResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Email"])

BASE_URL = "https://graph.microsoft.com/v1.0"


@router.get("/m365/status", response_model=M365StatusResponse)
async def get_m365_status(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get Microsoft 365 connection status.
    """
    try:
        if not current_user:
            return M365StatusResponse(connected=False)
        
        # Check if user has M365 tokens
        has_token = bool(
            current_user.microsoft_access_token and
            current_user.microsoft_refresh_token
        )
        
        if not has_token:
            return M365StatusResponse(connected=False)
        
        # Try to get access token to verify connection
        try:
            token = get_access_token()
            if token:
                # Make a simple API call to verify token works
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(
                    f"{BASE_URL}/me",
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code == 200:
                    user_data = response.json()
                    return M365StatusResponse(
                        connected=True,
                        last_sync=current_user.last_login.isoformat() if current_user.last_login else None,
                        expires_at=current_user.microsoft_token_expires_at.isoformat() if current_user.microsoft_token_expires_at else None,
                        account_type=getattr(current_user, 'account_type', None),
                        organization=user_data.get('mail', '').split('@')[1] if user_data.get('mail') else None
                    )
        except Exception as e:
            logger.warning(f"M365 token verification failed: {e}")
        
        return M365StatusResponse(connected=False)
    except Exception as e:
        logger.error(f"Error getting M365 status: {e}")
        return M365StatusResponse(connected=False)


@router.get("/emails", response_model=EmailsResponse)
async def get_emails(
    limit: int = Query(10, ge=1, le=50),
    folder: str = Query("inbox"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get recent emails from Microsoft 365.
    """
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for email access"
            )
        
        # Set session context so get_access_token can find user's tokens
        set_session_id(str(current_user.id))
        token = get_access_token()
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Microsoft 365 not connected. Please connect your account."
            )
        
        # Map folder names
        folder_map = {
            "inbox": "inbox",
            "sent": "sentitems",
            "drafts": "drafts",
            "archive": "archive",
            "deleted": "deleteditems"
        }
        folder_id = folder_map.get(folder.lower().strip(), "inbox")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get emails
        endpoint = f"{BASE_URL}/me/mailFolders/{folder_id}/messages"
        params = {
            "$select": "id,subject,from,receivedDateTime,isRead,bodyPreview",
            "$orderby": "receivedDateTime desc",
            "$top": limit
        }
        
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            logger.error(f"Error fetching emails: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching emails from Microsoft 365"
            )
        
        emails_data = response.json().get("value", [])
        
        # Get unread count
        unread_endpoint = f"{BASE_URL}/me/mailFolders/{folder_id}"
        unread_response = requests.get(unread_endpoint, headers=headers, timeout=5)
        unread_count = 0
        if unread_response.status_code == 200:
            unread_count = unread_response.json().get("unreadItemCount", 0)
        
        email_items = []
        for email in emails_data:
            from_info = email.get("from", {}).get("emailAddress", {})
            email_items.append(EmailItem(
                id=email.get("id", ""),
                subject=email.get("subject", "(No subject)"),
                from_address=from_info.get("address", ""),
                from_name=from_info.get("name"),
                received_date_time=email.get("receivedDateTime", ""),
                is_read=email.get("isRead", False),
                snippet=email.get("bodyPreview")
            ))
        
        return EmailsResponse(
            emails=email_items,
            total=len(email_items),
            unread_count=unread_count
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting emails: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving emails"
        )


@router.get("/emails/unread-count", response_model=UnreadCountResponse)
async def get_unread_count(
    folder: str = Query("inbox"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get unread email count.
    """
    try:
        if not current_user:
            return UnreadCountResponse(count=0)
        
        # Set session context so get_access_token can find user's tokens
        set_session_id(str(current_user.id))
        token = get_access_token()
        if not token:
            return UnreadCountResponse(count=0)
        
        folder_map = {
            "inbox": "inbox",
            "sent": "sentitems",
            "drafts": "drafts",
            "archive": "archive",
            "deleted": "deleteditems"
        }
        folder_id = folder_map.get(folder.lower().strip(), "inbox")
        
        headers = {"Authorization": f"Bearer {token}"}
        endpoint = f"{BASE_URL}/me/mailFolders/{folder_id}"
        
        response = requests.get(endpoint, headers=headers, timeout=5)
        
        if response.status_code == 200:
            unread_count = response.json().get("unreadItemCount", 0)
            return UnreadCountResponse(count=unread_count)
        
        return UnreadCountResponse(count=0)
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        return UnreadCountResponse(count=0)

