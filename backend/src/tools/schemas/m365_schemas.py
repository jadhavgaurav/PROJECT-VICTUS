from pydantic import BaseModel, Field
from typing import List, Optional

class ReadEmailsSchema(BaseModel):
    max_emails: int = Field(default=5, description="The maximum number of emails to read (default: 5).")
    folder: str = Field(default="inbox", description="The folder to read from (e.g., 'inbox', 'sent', 'drafts').")

class SendEmailSchema(BaseModel):
    to: str = Field(..., description="The recipient's email address.")
    subject: str = Field(..., description="The subject of the email.")
    content: str = Field(default="", description="The body content of the email.")

class GetCalendarEventsSchema(BaseModel):
    days: int = Field(default=7, description="Number of days to look ahead (default: 7).")
    specific_date: Optional[str] = Field(default=None, description="A specific date in YYYY-MM-DD format to check events for.")

class CreateCalendarEventSchema(BaseModel):
    subject: str = Field(..., description="The title of the event.")
    start_time_str: str = Field(..., description="The start time in natural language (e.g., 'today at 5pm').")
    end_time_str: str = Field(..., description="The end time in natural language (e.g., 'today at 6pm').")
    attendees: Optional[List[str]] = Field(default=None, description="List of email addresses to invite.")
    location: Optional[str] = Field(default=None, description="The location of the event.")
    body: Optional[str] = Field(default=None, description="Description or details of the event.")
    create_teams_meeting: bool = Field(default=False, description="Whether to create a Microsoft Teams meeting link.")
