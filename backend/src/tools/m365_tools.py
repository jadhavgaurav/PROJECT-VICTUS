"""
Microsoft 365 integration tools for email and calendar
"""

from typing import List, Optional
from datetime import datetime, timedelta, timezone
import requests  # type: ignore
import dateparser  # type: ignore

# Refactor: Use SafeTool and local schemas
from .base import SafeTool, RiskLevel
from .schemas.m365_schemas import (
    ReadEmailsSchema, SendEmailSchema,
    GetCalendarEventsSchema, CreateCalendarEventSchema
)
from ..m365_auth import get_access_token

BASE_URL = "https://graph.microsoft.com/v1.0"

# --- Core Function Implementations ---

def _read_emails(max_emails: int = 5, folder: str = "inbox") -> str:
    token = get_access_token()
    if not token:
        return "Authentication failed. The login process must be completed in the terminal."

    # Use a dictionary to map simple names to the official Microsoft Graph API folder IDs
    folder_map = {
        "inbox": "inbox",
        "sent": "sentitems",
        "drafts": "drafts",
        "archive": "archive",
        "deleted": "deleteditems"
    }
    folder_id = folder_map.get(folder.lower().strip(), "inbox")

    headers = {"Authorization": f"Bearer {token}"}
    endpoint = f"{BASE_URL}/me/mailFolders/{folder_id}/messages?$select=subject,from,receivedDateTime&$orderby=receivedDateTime desc&$top={max_emails}"
    
    response = requests.get(endpoint, headers=headers)
    
    if response.status_code == 200:
        emails = response.json().get("value", [])
        if not emails:
            return f"The '{folder_id}' folder is empty."
        summaries = [f"From: {e['from']['emailAddress']['name']}\nSubject: {e['subject']}" for e in emails]
        return "\n\n---\n\n".join(summaries)
    
    return f"Error reading emails from folder '{folder_id}': {response.text}"

def _send_email(to: str, subject: str, content: str = "") -> str:
    token = get_access_token()
    if not token:
        return "Authentication failed. The login process must be completed in the terminal."

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    email_data = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": content},
            "toRecipients": [{"emailAddress": {"address": to}}]
        },
        "saveToSentItems": "true"
    }
    response = requests.post(f"{BASE_URL}/me/sendMail", headers=headers, json=email_data)
    return "Email sent successfully." if response.status_code == 202 else f"Error sending email: {response.text}"

def _get_calendar_events(days: int = 7, specific_date: Optional[str] = None) -> str:
    token = get_access_token()
    if not token:
        return "Authentication failed. The login process must be completed in the terminal."

    headers = {"Authorization": f"Bearer {token}"}
    
    if specific_date:
        try:
            start_dt = datetime.strptime(specific_date, "%Y-%m-%d")
            end_dt = start_dt + timedelta(days=1)
            start_time = start_dt.isoformat() + "Z"
            end_time = end_dt.isoformat() + "Z"
        except ValueError:
            return "Error: Please provide the specific_date in YYYY-MM-DD format."
    else:
        start_time = datetime.utcnow().isoformat() + "Z"
        end_time = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"

    params = {
        'startDateTime': start_time,
        'endDateTime': end_time,
        '$select': 'subject,start,end',
        '$orderby': 'start/dateTime'
    }
    response = requests.get(f"{BASE_URL}/me/calendarview", headers=headers, params=params)
    
    if response.status_code == 200:
        events = response.json().get("value", [])
        if not events:
            return f"No events found for the specified period."
        
        # Format events with proper timezone conversion
        details = []
        for e in events:
            # Parse UTC datetime from Microsoft Graph
            start_utc_str = e['start']['dateTime']
            if start_utc_str.endswith('Z'):
                start_utc_str = start_utc_str[:-1] + '+00:00'
            
            try:
                # Parse the datetime (handle both with and without timezone info)
                if '+' in start_utc_str or start_utc_str.endswith('Z'):
                    # Has timezone info
                    start_dt = datetime.fromisoformat(start_utc_str.replace('Z', '+00:00'))
                else:
                    # Assume UTC if no timezone
                    start_dt = datetime.fromisoformat(start_utc_str)
                    start_dt = start_dt.replace(tzinfo=timezone.utc)
                
                # Convert to local time
                local_dt = start_dt.astimezone()
                
                # Format nicely
                formatted_time = local_dt.strftime("%B %d, %Y, at %I:%M %p")
                details.append(f"- {e['subject']} starting at {formatted_time}")
            except Exception as parse_err:
                # Fallback to raw datetime if parsing fails
                details.append(f"- {e['subject']} starting at {e['start']['dateTime']}")
        
        return "Here are the matching events:\n" + "\n".join(details)
    return f"Error getting calendar events: {response.text}"

def _create_calendar_event(
    subject: str,
    start_time_str: str,
    end_time_str: str,
    attendees: Optional[List[str]] = None,
    location: Optional[str] = None,
    body: Optional[str] = None,
    create_teams_meeting: bool = False
) -> str:
    token = get_access_token()
    if not token:
        return "Authentication failed. The login process must be completed in the terminal."

    try:
        start_dt = dateparser.parse(start_time_str)
        end_dt = dateparser.parse(end_time_str)

        if not start_dt or not end_dt:
            return "Error: Could not understand the start or end time. Please be more specific (e.g., 'today at 5pm', 'August 29 2025 at 10am')."

        # Convert the parsed local time to UTC for the API
        start_utc = start_dt.astimezone(timezone.utc)
        end_utc = end_dt.astimezone(timezone.utc)
    except Exception as e:
        return f"Error parsing date/time: {e}. Please use a clearer format."

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    event_data = {
        "subject": subject,
        "start": {"dateTime": start_utc.isoformat(), "timeZone": "UTC"},
        "end": {"dateTime": end_utc.isoformat(), "timeZone": "UTC"},
        "isOnlineMeeting": create_teams_meeting,
        "onlineMeetingProvider": "teamsForBusiness" if create_teams_meeting else "unknown"
    }

    if attendees:
        event_data["attendees"] = [
            {"emailAddress": {"address": email.strip()}, "type": "required"}
            for email in attendees
        ]

    if location:
        event_data["location"] = {"displayName": location}
    
    if body:
        event_data["body"] = {"contentType": "Text", "content": body}

    response = requests.post(f"{BASE_URL}/me/events", headers=headers, json=event_data)

    if response.status_code == 201:
        if attendees:
            return f"Successfully created event '{subject}' and sent invitations to {', '.join(attendees)}."
        return f"Successfully created calendar event: '{subject}'."
    
    return f"Error creating calendar event: {response.status_code} - {response.text}"

# --- Tool Construction ---

read_emails = SafeTool.from_func(
    func=_read_emails,
    name="read_emails",
    description="Reads emails from a specified folder in the user's Microsoft Outlook account.",
    args_schema=ReadEmailsSchema,
    risk_level=RiskLevel.MEDIUM
)

send_email = SafeTool.from_func(
    func=_send_email,
    name="send_email",
    description="Sends an email from the user's Microsoft Outlook account.",
    args_schema=SendEmailSchema,
    risk_level=RiskLevel.HIGH
)

get_calendar_events = SafeTool.from_func(
    func=_get_calendar_events,
    name="get_calendar_events",
    description="Gets events from the user's Microsoft Outlook calendar.",
    args_schema=GetCalendarEventsSchema,
    risk_level=RiskLevel.MEDIUM
)

create_calendar_event = SafeTool.from_func(
    func=_create_calendar_event,
    name="create_calendar_event",
    description="Creates a new event in the user's Outlook calendar.",
    args_schema=CreateCalendarEventSchema,
    risk_level=RiskLevel.HIGH
)
