from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...database import get_db
from ...models import Trace, TraceStep

router = APIRouter(prefix="/traces", tags=["Traces"])

@router.get("/")
def get_traces(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    """List recent execution traces."""
    return db.query(Trace).order_by(Trace.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{trace_id}")
def get_trace_details(trace_id: str, db: Session = Depends(get_db)):
    """Get full details of a specific trace including steps."""
    trace = db.query(Trace).filter(Trace.id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    
    steps = db.query(TraceStep).filter(TraceStep.trace_id == trace_id).order_by(TraceStep.timestamp).all()
    return {"trace": trace, "steps": steps}

@router.post("/{trace_id}/replay")
def replay_trace(trace_id: str):
    """
    Replay a trace in dry-run mode (simulated execution).
    (Placeholder implementation for now)
    """
    # Logic to fetch trace, iterate steps, and call tools in dry-run mode
    return {"message": "Replay functionality coming soon", "trace_id": trace_id}
