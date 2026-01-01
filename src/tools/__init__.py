"""
Tools module for Project VICTUS
Provides modular tool implementations for the AI agent
"""

from .assembler import get_all_tools, FAISS_INDEX_PATH, update_vector_store
from .config import async_client
from .web_search import web_search_tool
from .system_tools import (
    list_files,
    open_app,
    get_clipboard_content,
    take_screenshot,
    type_text,
    get_active_window_title
)
from .m365_tools import (
    read_emails,
    send_email,
    get_calendar_events,
    create_calendar_event
)
from .weather_tool import get_weather_info
from .memory_tools import remember_fact, recall_fact
from .rag_tools import query_uploaded_documents

__all__ = [
    "get_all_tools",
    "FAISS_INDEX_PATH",
    "update_vector_store",
    "async_client",
    "web_search_tool",
    "list_files",
    "open_app",
    "get_clipboard_content",
    "take_screenshot",
    "type_text",
    "get_active_window_title",
    "read_emails",
    "send_email",
    "get_calendar_events",
    "create_calendar_event",
    "get_weather_info",
    "remember_fact",
    "recall_fact",
    "query_uploaded_documents",
]

