"""
Health check and monitoring endpoints
"""

from fastapi import APIRouter, Request
from ..database import engine
from ..utils.metrics import get_metrics_response

router = APIRouter(tags=["Health", "Monitoring"])


@router.get("/healthz")
async def health_check(request: Request):
    """
    Health check endpoint with detailed status.
    
    Returns:
        - status: Overall health status
        - version: Application version
        - database: Database connection status
        - models: Status of loaded ML models
    """
    health_status = {
        "status": "ok",
        "version": "2.0.0",
        "database": "connected" if engine else "disconnected",
        "models": {}
    }
    
    # Check model status
    if hasattr(request.app.state, 'stt_model') and request.app.state.stt_model:
        health_status["models"]["stt"] = "loaded"
    else:
        health_status["models"]["stt"] = "not_loaded"
    
    if hasattr(request.app.state, 'tts_model') and request.app.state.tts_model:
        health_status["models"]["tts"] = "loaded"
    else:
        health_status["models"]["tts"] = "not_loaded"
    
    if hasattr(request.app.state, 'agent_executor') and request.app.state.agent_executor:
        health_status["models"]["agent"] = "ready"
    else:
        health_status["models"]["agent"] = "not_ready"
    
    return health_status


@router.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint.
    
    Returns metrics in Prometheus format for monitoring.
    """
    return get_metrics_response()

