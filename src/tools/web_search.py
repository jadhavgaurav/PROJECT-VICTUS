"""
Web search tools using Tavily
"""

from langchain_community.tools.tavily_search import TavilySearchResults
from ..config import settings

# Initialize web search tool only if API key is available
# Wrap in try-except to handle validation errors gracefully
web_search_tool = None
if settings.TAVILY_API_KEY and settings.TAVILY_API_KEY.strip():
    try:
        # TavilySearchResults can also read from environment, but we'll pass it explicitly
        import os
        # Temporarily set environment variable for Tavily
        os.environ['TAVILY_API_KEY'] = settings.TAVILY_API_KEY
        web_search_tool = TavilySearchResults(
            k=3,
            tavily_api_key=settings.TAVILY_API_KEY
        )
    except Exception as e:
        # If initialization fails, web_search_tool remains None
        # This allows the app to start even if Tavily is misconfigured
        import warnings
        warnings.warn(f"Failed to initialize Tavily search tool: {e}. Web search will be disabled.")
        web_search_tool = None

