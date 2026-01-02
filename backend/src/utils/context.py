"""
Context management for request-scoped data
"""

from contextvars import ContextVar
from typing import Optional

# Context variable for storing current user/session ID
current_session_id: ContextVar[Optional[str]] = ContextVar('current_session_id', default=None)

# Context variable for storing trace ID
current_trace_id: ContextVar[Optional[str]] = ContextVar('current_trace_id', default=None)

def set_session_id(session_id: Optional[str]) -> None:
    """Set the current session ID in context."""
    if session_id:
        current_session_id.set(session_id)
    else:
        current_session_id.set(None)

def get_session_id() -> Optional[str]:
    """Get the current session ID from context."""
    return current_session_id.get()

def set_trace_id(trace_id: Optional[str]) -> None:
    """Set the current trace ID in context."""
    current_trace_id.set(trace_id)

def get_trace_id() -> Optional[str]:
    """Get the current trace ID from context."""
    return current_trace_id.get()

def get_user_id() -> str:
    """
    Get user ID from context.
    Uses session_id as user_id for now (can be extended for multi-user).
    Note: This is used by tools. For authenticated users, user_id should come from the User model.
    """
    session_id = get_session_id()
    if session_id:
        # For now, use session_id as user_id
        # In production, you might want to map session_id to actual user_id
        return session_id
    return "default_user"


