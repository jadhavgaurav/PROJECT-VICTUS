from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from ...database import get_db
from ...models import PendingAction, TraceStep
from ...tools.registry import ToolRegistry
from ...utils.logging import get_logger

router = APIRouter(prefix="/approvals", tags=["Approvals"])
logger = get_logger(__name__)

@router.get("/pending")
def get_pending_actions(db: Session = Depends(get_db)):
    """List all pending actions requiring approval."""
    return db.query(PendingAction).filter(PendingAction.status == "PENDING").all()

@router.post("/{action_id}/approve")
async def approve_action(
    action_id: str, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Approve a pending action.
    Executes the tool immediately and records the result.
    """
    action = db.query(PendingAction).filter(PendingAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    if action.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Action is already {action.status}")

    # Mark as APPROVED
    action.status = "APPROVED"
    db.commit()

    # Execute the tool
    try:
        tool = ToolRegistry.get_tool(action.tool_name)
        args = json.loads(action.args)
        
        # Execute the underlying function directly to bypass policy check
        # This assumes _func is available (from SafeTool factory)
        if hasattr(tool, "_func"):
             # If async, we should await it?
             # For now, simplistic sync call or handle potential async
             # Most of our tools are sync, except weather which is async.
             import inspect
             if inspect.iscoroutinefunction(tool._func):
                 result = await tool._func(**args)
             else:
                 result = tool._func(**args)
        else:
            # Fallback (risky if it triggers policy again)
            result = tool.invoke(args)

        # Log to trace (if trace_id exists in some context, but here we might just log simple result)
        # Ideally we update the original TraceStep or creaet a new one?
        # For simplicity, we just log it.
        logger.info(f"Action {action_id} approved and executed. Result: {result}")
        
        return {"status": "executed", "result": result}

    except Exception as e:
        logger.error(f"Error executing approved action {action_id}: {e}")
        # Optionally verify if we should mark it as failed?
        return {"status": "error", "message": str(e)}

@router.post("/{action_id}/deny")
def deny_action(action_id: str, db: Session = Depends(get_db)):
    """Deny a pending action."""
    action = db.query(PendingAction).filter(PendingAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    action.status = "DENIED"
    db.commit()
    return {"status": "denied"}
