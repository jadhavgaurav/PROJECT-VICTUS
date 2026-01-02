"""
Prometheus metrics for monitoring
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
from typing import Optional

# Request metrics
http_requests_total = Counter(
    'victus_http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'victus_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Agent metrics
agent_invocations_total = Counter(
    'victus_agent_invocations_total',
    'Total number of agent invocations',
    ['status']
)

agent_response_time = Histogram(
    'victus_agent_response_time_seconds',
    'Agent response time in seconds'
)

# Tool metrics
tool_invocations_total = Counter(
    'victus_tool_invocations_total',
    'Total number of tool invocations',
    ['tool_name', 'status']
)

# System metrics
active_sessions = Gauge(
    'victus_active_sessions',
    'Number of active chat sessions'
)

vector_store_size = Gauge(
    'victus_vector_store_size',
    'Number of documents in vector store'
)

def get_metrics_response() -> Response:
    """Get Prometheus metrics as HTTP response."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )

