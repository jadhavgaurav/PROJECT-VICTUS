"""
Tool assembler - combines all tools into a single list for the agent
"""

from typing import List
import os

from .web_search import web_search_tool
from .system_tools import (
    list_files,
    open_app,
    get_clipboard_content,
    take_screenshot,
    type_text,
    get_active_window_title,
    get_system_info
)
from .m365_tools import (
    read_emails,
    send_email,
    get_calendar_events,
    create_calendar_event
)
from .weather_tool import get_weather_info
from .config import async_client
from .memory_tools import remember_fact, recall_fact
from .rag_tools import query_uploaded_documents, FAISS_INDEX_PATH, update_vector_store

def get_all_tools(rag_enabled: bool) -> List:
    """Dynamically assembles the list of available tools."""
    all_tools = [
        list_files,
        open_app,
        get_weather_info,
        get_clipboard_content,
        take_screenshot,
        type_text,
        get_active_window_title,
        get_system_info,
        remember_fact,
        recall_fact
    ]
    
    # Add web search if available
    if web_search_tool:
        all_tools.append(web_search_tool)
    
    # Add RAG tool if enabled
    if rag_enabled:
        all_tools.append(query_uploaded_documents)
    
    # Always include the M365 tools
    all_tools.extend([
        read_emails,
        send_email,
        get_calendar_events,
        create_calendar_event
    ])
    
    # Register all tools
    from .registry import ToolRegistry
    for tool in all_tools:
        ToolRegistry.register(tool)
        
    return all_tools

