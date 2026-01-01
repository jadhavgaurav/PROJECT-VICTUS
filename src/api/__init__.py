"""
API routes module for Project VICTUS
"""

from .health import router as health_router
from .chat import router as chat_router
from .documents import router as documents_router
from .voice import router as voice_router
from .pages import router as pages_router
from .conversations import router as conversations_router
from .facts import router as facts_router
from .email import router as email_router
from .calendar import router as calendar_router
from .stats import router as stats_router

__all__ = [
    "health_router",
    "chat_router",
    "documents_router",
    "voice_router",
    "pages_router",
    "conversations_router",
    "facts_router",
    "email_router",
    "calendar_router",
    "stats_router",
]

