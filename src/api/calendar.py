"""
Calendar integration endpoints (Microsoft 365)
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import requests

from ..database import get_db
from ..models import User
from ..auth.dependencies import get_optional_user
from ..m365_auth import get_access_token
from ..utils.logging import get_logger
from ..utils.context import set_session_id
from .schemas import CalendarEventsResponse, CalendarEventItem

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Calendar"])

BASE_URL = "https://graph.microsoft.com/v1.0"


@router.get("/calendar/events", response_model=CalendarEventsResponse)
async def get_calendar_events(
    days: int = Query(7, ge=1, le=30),
    start_date: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get calendar events from Microsoft 365.
    """
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for calendar access"
            )
        
        # Set session context so get_access_token can find user's tokens
        set_session_id(str(current_user.id))
        token = get_access_token()
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Microsoft 365 not connected. Please connect your account."
            )
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Calculate time range
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                end_dt = start_dt + timedelta(days=1)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid date format. Use YYYY-MM-DD"
                )
        else:
            start_dt = datetime.utcnow()
            end_dt = start_dt + timedelta(days=days)
        
        start_time = start_dt.isoformat() + "Z"
        end_time = end_dt.isoformat() + "Z"
        
        params = {
            'startDateTime': start_time,
            'endDateTime': end_time,
            '$select': 'id,subject,start,end,location,attendees,isAllDay,organizer',
            '$orderby': 'start/dateTime',
            '$top': limit
        }
        
        response = requests.get(
            f"{BASE_URL}/me/calendarview",
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"Error fetching calendar events: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching calendar events from Microsoft 365"
            )
        
        events_data = response.json().get("value", [])
        
        event_items = []
        for event in events_data:
            # Extract attendees
            attendees = []
            for attendee in event.get("attendees", []):
                email = attendee.get("emailAddress", {}).get("address", "")
                if email:
                    attendees.append(email)
            
            # Extract organizer
            organizer = None
            if event.get("organizer"):
                organizer = event.get("organizer", {}).get("emailAddress", {}).get("address")
            
            event_items.append(CalendarEventItem(
                id=event.get("id", ""),
                subject=event.get("subject", "(No subject)"),
                start=event.get("start", {}).get("dateTime", ""),
                end=event.get("end", {}).get("dateTime", ""),
                location=event.get("location", {}).get("displayName") if event.get("location") else None,
                attendees=attendees,
                is_all_day=event.get("isAllDay", False),
                organizer=organizer
            ))
        
        return CalendarEventsResponse(
            events=event_items,
            total=len(event_items)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving calendar events"
        )


@router.get("/calendar/upcoming", response_model=CalendarEventsResponse)
async def get_upcoming_events(
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get next N upcoming calendar events.
    """
    try:
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required for calendar access"
            )
        
        # Set session context so get_access_token can find user's tokens
        set_session_id(str(current_user.id))
        token = get_access_token()
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Microsoft 365 not connected. Please connect your account."
            )
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get events from now to 30 days ahead
        start_time = datetime.utcnow().isoformat() + "Z"
        end_time = (datetime.utcnow() + timedelta(days=30)).isoformat() + "Z"
        
        params = {
            'startDateTime': start_time,
            'endDateTime': end_time,
            '$select': 'id,subject,start,end,location,attendees,isAllDay,organizer',
            '$orderby': 'start/dateTime',
            '$top': limit
        }
        
        response = requests.get(
            f"{BASE_URL}/me/calendarview",
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"Error fetching upcoming events: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error fetching upcoming calendar events"
            )
        
        events_data = response.json().get("value", [])
        
        event_items = []
        for event in events_data:
            attendees = []
            for attendee in event.get("attendees", []):
                email = attendee.get("emailAddress", {}).get("address", "")
                if email:
                    attendees.append(email)
            
            organizer = None
            if event.get("organizer"):
                organizer = event.get("organizer", {}).get("emailAddress", {}).get("address")
            
            event_items.append(CalendarEventItem(
                id=event.get("id", ""),
                subject=event.get("subject", "(No subject)"),
                start=event.get("start", {}).get("dateTime", ""),
                end=event.get("end", {}).get("dateTime", ""),
                location=event.get("location", {}).get("displayName") if event.get("location") else None,
                attendees=attendees,
                is_all_day=event.get("isAllDay", False),
                organizer=organizer
            ))
        
        return CalendarEventsResponse(
            events=event_items,
            total=len(event_items)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting upcoming events: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving upcoming calendar events"
        )

