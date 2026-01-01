"""
Tests for metrics
"""

import pytest
from src.utils.metrics import (
    http_requests_total,
    agent_invocations_total,
    get_metrics_response
)

def test_metrics_response():
    """Test metrics endpoint response."""
    response = get_metrics_response()
    assert response.status_code == 200
    assert "text/plain" in response.media_type
    assert len(response.body) > 0

def test_http_requests_counter():
    """Test HTTP requests counter."""
    initial_count = http_requests_total._value.get()
    http_requests_total.labels(method="GET", endpoint="/test", status=200).inc()
    new_count = http_requests_total._value.get()
    assert new_count > initial_count

