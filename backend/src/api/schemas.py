"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field, field_validator
from ..utils.security import validate_input, validate_session_id


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        return validate_input(v)
    
    # Simple validation for UUID format could be added here
    
class HistoryRequest(BaseModel):
    """Request schema for history endpoint."""
    conversation_id: str = Field(..., min_length=1, max_length=100)


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""
    status: str
    version: str
    database: str
    models: dict


class UploadResponse(BaseModel):
    """Response schema for document upload endpoint."""
    status: str
    filename: str
    detail: str


class TranscriptionResponse(BaseModel):
    """Response schema for transcription endpoint."""
    transcription: str


class SynthesisResponse(BaseModel):
    """Response schema for speech synthesis endpoint."""
    audio_url: str


# Conversation schemas
class ConversationItem(BaseModel):
    """Schema for a conversation item."""
    session_id: str
    title: str | None
    last_message: str | None
    timestamp: str
    message_count: int
    created_at: str | None = None


class ConversationsResponse(BaseModel):
    """Response schema for conversations list."""
    conversations: list[ConversationItem]
    total: int


class ConversationTitleUpdate(BaseModel):
    """Request schema for updating conversation title."""
    title: str = Field(..., min_length=1, max_length=200)


# Document schemas
class DocumentItem(BaseModel):
    """Schema for a document item."""
    filename: str
    size: int | None
    upload_date: str
    status: str  # processing, ready, error
    indexed: bool


class DocumentsResponse(BaseModel):
    """Response schema for documents list."""
    documents: list[DocumentItem]
    total: int
    total_size: int


class DocumentStatusResponse(BaseModel):
    """Response schema for document status."""
    total: int
    indexed: int
    processing: int
    failed: int


# Facts schemas
class FactItem(BaseModel):
    """Schema for a fact item."""
    id: int
    key: str
    value: str
    last_updated: str


class FactsResponse(BaseModel):
    """Response schema for facts list."""
    facts: list[FactItem]
    total: int


class FactCreate(BaseModel):
    """Request schema for creating a fact."""
    key: str = Field(..., min_length=1, max_length=200)
    value: str = Field(..., min_length=1, max_length=5000)
    
    @field_validator('key', 'value')
    @classmethod
    def validate_input(cls, v: str) -> str:
        return validate_input(v)


class FactUpdate(BaseModel):
    """Request schema for updating a fact."""
    key: str | None = Field(None, min_length=1, max_length=200)
    value: str | None = Field(None, min_length=1, max_length=5000)
    
    @field_validator('key', 'value')
    @classmethod
    def validate_input(cls, v: str | None) -> str | None:
        if v is not None:
            return validate_input(v)
        return v


class FactsImport(BaseModel):
    """Request schema for importing facts."""
    facts: list[dict[str, str]] = Field(..., min_length=1)


class FactsImportResponse(BaseModel):
    """Response schema for facts import."""
    imported: int
    failed: int
    errors: list[str] = []


# Email schemas
class EmailItem(BaseModel):
    """Schema for an email item."""
    id: str
    subject: str
    from_address: str
    from_name: str | None
    received_date_time: str
    is_read: bool
    snippet: str | None = None


class EmailsResponse(BaseModel):
    """Response schema for emails list."""
    emails: list[EmailItem]
    total: int
    unread_count: int


class UnreadCountResponse(BaseModel):
    """Response schema for unread email count."""
    count: int


# Calendar schemas
class CalendarEventItem(BaseModel):
    """Schema for a calendar event item."""
    id: str
    subject: str
    start: str
    end: str
    location: str | None = None
    attendees: list[str] = []
    is_all_day: bool = False
    organizer: str | None = None


class CalendarEventsResponse(BaseModel):
    """Response schema for calendar events list."""
    events: list[CalendarEventItem]
    total: int


# M365 Status schema
class M365StatusResponse(BaseModel):
    """Response schema for M365 connection status."""
    connected: bool
    last_sync: str | None = None
    expires_at: str | None = None
    account_type: str | None = None
    organization: str | None = None


# Stats schemas
class UsageStatsResponse(BaseModel):
    """Response schema for usage statistics."""
    total_messages: int
    total_conversations: int
    documents_uploaded: int
    facts_stored: int
    api_calls: int | None = None
    usage_by_date: list[dict[str, int | str]] = []

