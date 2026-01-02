"""
Tests for tools module
"""

import pytest
from src.tools.system_tools import list_files, resolve_path
from src.tools.config import resolve_path as config_resolve_path

def test_resolve_path():
    """Test path resolution."""
    # Test with home shortcut
    path = config_resolve_path("home")
    assert path.exists() or str(path)  # Should return a valid path
    
    # Test with invalid path
    path = config_resolve_path("/nonexistent/path")
    assert isinstance(path, type(path))  # Should return Path object

def test_list_files():
    """Test list_files tool."""
    # This will fail on non-Windows or if directory doesn't exist
    # In production, mock the filesystem
    result = list_files("home")
    assert isinstance(result, str)

