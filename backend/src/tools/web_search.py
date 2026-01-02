"""
Web search tools using Tavily
"""

from typing import Optional
from pydantic import BaseModel, Field
from langchain_community.tools.tavily_search import TavilySearchResults
from ..config import settings
from .base import SafeTool, RiskLevel

class WebSearchSchema(BaseModel):
    query: str = Field(..., description="The search query.")

def _get_web_search_tool() -> Optional[SafeTool]:
    """
    Initializes and returns the Web Search SafeTool if API key is present.
    """
    if not (settings.TAVILY_API_KEY and settings.TAVILY_API_KEY.strip()):
        import warnings
        warnings.warn("Tavily API key not found. Web search disabled.")
        return None

    try:
        import os
        os.environ['TAVILY_API_KEY'] = settings.TAVILY_API_KEY
        
        # Initialize the underlying Tavily tool
        tavily_tool = TavilySearchResults(
            k=3,
            tavily_api_key=settings.TAVILY_API_KEY
        )
        
        # Define a wrapper function for SafeTool
        def _search_wrapper(query: str):
            # This calls the tool's invoke method
            return tavily_tool.invoke(query)
            
        return SafeTool.from_func(
            func=_search_wrapper,
            name="web_search",
            description="Performs a web search to find information.",
            args_schema=WebSearchSchema,
            risk_level=RiskLevel.LOW
        )
        
    except Exception as e:
        import warnings
        warnings.warn(f"Failed to initialize Tavily search tool: {e}. Web search will be disabled.")
        return None

# Single instance export
web_search_tool = _get_web_search_tool()
