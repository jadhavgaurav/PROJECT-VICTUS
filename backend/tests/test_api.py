"""
Tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from src.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "database" in data
    assert "models" in data

def test_metrics_endpoint():
    """Test metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")

def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code in [200, 404]  # 404 if static files don't exist

def test_chat_endpoint_invalid_auth():
    """Test chat endpoint without auth should fail."""
    response = client.post(
        "/api/chat",
        json={"message": "hello", "conversation_id": "test"}
    )
    # Should fail auth
    assert response.status_code == 401

def test_history_endpoint_no_auth():
    """Test history endpoint without auth should fail."""
    response = client.post(
        "/api/history",
        json={"conversation_id": "test_session"}
    )
    assert response.status_code == 401

def test_upload_endpoint_invalid_file():
    """Test upload endpoint with invalid file."""
    response = client.post(
        "/api/upload",
        files={"file": ("test.txt", b"test content", "text/plain")}
    )
    assert response.status_code == 400

