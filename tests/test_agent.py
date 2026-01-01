"""
Tests for agent module
"""

import pytest
from unittest.mock import Mock, patch
from src.agent import create_agent_executor

def test_create_agent_executor():
    """Test agent executor creation."""
    with patch('src.agent.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = "test_key"
        with patch('src.agent.ChatOpenAI'):
            with patch('src.agent.get_all_tools', return_value=[]):
                executor = create_agent_executor(rag_enabled=False)
                assert executor is not None

def test_create_agent_executor_with_rag():
    """Test agent executor creation with RAG enabled."""
    with patch('src.agent.settings') as mock_settings:
        mock_settings.OPENAI_API_KEY = "test_key"
        with patch('src.agent.ChatOpenAI'):
            with patch('src.agent.get_all_tools', return_value=[]):
                executor = create_agent_executor(rag_enabled=True)
                assert executor is not None

