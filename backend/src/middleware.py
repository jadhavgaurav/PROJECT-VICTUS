import uuid
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Trace
from .utils.context import set_trace_id, get_user_id
from .utils.logging import get_logger

logger = get_logger(__name__)

class TraceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate or retrieve Trace ID
        trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
        set_trace_id(trace_id)
        
        # Log start of trace to DB (async-ish via sync Session)
        # We need to capture the input (URL/Body) if possible, but body is stream.
        # For now, just create the Trace record.
        try:
            db: Session = SessionLocal()
            user_id = get_user_id() or "anonymous"
            
            # Check if trace already exists (if passed in header)
            existing_trace = db.query(Trace).filter(Trace.id == trace_id).first()
            if not existing_trace:
                new_trace = Trace(id=trace_id, user_id=user_id, input_text=str(request.url))
                db.add(new_trace)
                db.commit()
            db.close()
        except Exception as e:
            logger.error(f"Failed to create trace record: {e}")

        response = await call_next(request)
        
        response.headers["X-Trace-Id"] = trace_id
        return response
