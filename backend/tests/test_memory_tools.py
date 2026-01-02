"""
Tests for memory tools
"""

import pytest
from unittest.mock import Mock, patch
from src.tools.memory_tools import remember_fact, recall_fact
from src.utils.context import set_session_id, get_user_id

def test_get_user_id_from_session():
    """Test user ID extraction from session."""
    set_session_id("test_session_123")
    user_id = get_user_id()
    assert user_id == "test_session_123"

def test_get_user_id_default():
    """Test default user ID when no session."""
    # Clear context
    set_session_id(None)
    user_id = get_user_id()
    assert user_id == "default_user"

def test_remember_fact():
    """Test remembering a fact."""
    set_session_id("test_session")
    with patch('src.tools.memory_tools.SessionLocal') as mock_session:
        mock_db = Mock()
        mock_session.return_value.__enter__ = Mock(return_value=mock_db)
        mock_session.return_value.__exit__ = Mock(return_value=None)
        mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_db.add = Mock()
        mock_db.commit = Mock()
        
        result = remember_fact("favorite_color", "blue")
        assert "Remembered" in result or "Updated" in result

