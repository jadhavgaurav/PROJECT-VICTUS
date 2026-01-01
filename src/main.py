"""
Main FastAPI application for Project VICTUS
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

# Local Imports
from .database import init_db
from .tools.config import async_client
from .config import settings
from .utils.logging import get_logger, setup_logging
from .utils.security import setup_cors, setup_rate_limiting
from .utils.metrics import (
    http_requests_total,
    http_request_duration,
)
from .auth import router as auth_router
from .api import (
    health_router,
    chat_router,
    documents_router,
    voice_router,
    pages_router,
    conversations_router,
    facts_router,
    email_router,
    calendar_router,
    stats_router,
)

logger = get_logger(__name__)

# Initialize Database
init_db()

# Lifespan manager for loading models on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load all necessary models and the agent when the application starts.
    """
    logger.info("--- Application Startup ---")
    
    # Validate settings
    try:
        settings.validate_settings()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise
    
    logger.info(f"Database URL: {settings.DATABASE_URL}")

    # Load Speech-to-Text Model
    try:
        from faster_whisper import WhisperModel
        logger.info("Loading STT model (faster-whisper)...")
        app.state.stt_model = WhisperModel("base.en", device="cpu", compute_type="int8")
        logger.info("STT model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load STT model: {e}")
        app.state.stt_model = None

    # Load Text-to-Speech Model
    try:
        from piper import PiperVoice
        model_path = next(
            (os.path.join("models", f) for f in os.listdir("models") if f.endswith(".onnx")),
            None
        )
        if not model_path:
            logger.warning("Could not find a .onnx model file in the /models directory.")
            app.state.tts_model = None
        else:
            logger.info(f"Loading TTS model ({model_path})...")
            app.state.tts_model = PiperVoice.load(model_path)
            logger.info("TTS model loaded successfully.")
    except Exception as e:
        logger.error(f"Failed to load TTS model: {e}")
        app.state.tts_model = None

    # Create a reusable Agent Executor
    logger.info("Creating initial Agent Executor...")
    try:
        from .agent import create_agent_executor
        app.state.agent_executor = create_agent_executor(rag_enabled=False)
        logger.info("Initial Agent Executor created successfully.")
    except Exception as e:
        logger.error(f"Failed to create agent executor: {e}")
        raise
    
    logger.info("--- Application Ready ---")
    
    yield  # The application is now running

    # --- Shutdown logic ---
    logger.info("--- Application Shutdown ---")
    try:
        await async_client.aclose()
        logger.info("Async HTTP Client closed.")
    except Exception as e:
        logger.error(f"Error closing async client: {e}")

# Create FastAPI app
app = FastAPI(
    title="Project VICTUS",
    description="Advanced AI Personal Assistant",
    version="2.0.0",
    lifespan=lifespan
)

# Setup CORS and Rate Limiting
setup_cors(app)
setup_rate_limiting(app)

# Include all API routers
app.include_router(auth_router)
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(voice_router)
app.include_router(pages_router)
app.include_router(conversations_router)
app.include_router(facts_router)
app.include_router(email_router)
app.include_router(calendar_router)
app.include_router(stats_router)

# Mount static files (for frontend)
static_dir = "static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to collect HTTP metrics."""
    import time
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    http_request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
