from typing import Dict, List, Type
from .base import SafeTool

class ToolRegistry:
    _registry: Dict[str, SafeTool] = {}

    @classmethod
    def register(cls, tool: SafeTool):
        """Registers a SafeTool instance."""
        if tool.name in cls._registry:
            # We might want to allow overwrites or log a warning
            pass 
        cls._registry[tool.name] = tool

    @classmethod
    def get_tool(cls, name: str) -> SafeTool:
        """Retrieves a tool by name."""
        if name not in cls._registry:
            raise ValueError(f"Tool {name} not found in registry")
        return cls._registry[name]

    @classmethod
    def get_all_tools(cls) -> List[SafeTool]:
        """Returns all registered tools."""
        return list(cls._registry.values())

    @classmethod
    def clear(cls):
        """Clears the registry (useful for testing)."""
        cls._registry.clear()
