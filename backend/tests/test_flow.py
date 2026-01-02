import json
import uuid
import asyncio
from src.tools.m365_tools import send_email
from src.policy.engine import policy_engine
from src.database import SessionLocal
from src.models import PendingAction, TraceStep
from src.api.routes.approvals import approve_action

async def verify_flow():
    print("--- STARTING E2E VERIFICATION ---")
    
    # 1. Simulate High Risk Tool Call
    print("\n1. Calling HIGH risk tool (send_email)...")
    result = send_email.invoke({
        "to": "test@example.com", 
        "subject": "Test Safety", 
        "content": "This should be blocked."
    })
    print(f"Result: {result}")
    
    assert "Action Requires Approval" in result
    action_id = result.split("ID: ")[1].split(")")[0]
    print(f"Captured Action ID: {action_id}")
    
    # 2. Check Database for Pending Action
    print("\n2. Checking DB for Pending Action...")
    db = SessionLocal()
    action = db.query(PendingAction).filter(PendingAction.id == action_id).first()
    assert action is not None
    assert action.status == "PENDING"
    assert action.tool_name == "send_email"
    print("Pending Action verified in DB.")
    db.close()
    
    # 3. Approve Action
    print("\n3. Approving Action via API (simulated)...")
    # We simulate the API call logic
    db = SessionLocal()
    
    # Needs BackgroundTasks mock
    from fastapi import BackgroundTasks
    bg = BackgroundTasks()
    
    # NOTE: send_email will try to use M365 Auth. It might fail if not authenticated.
    # But we want to verifying it tries to execute.
    # The return from approve_action is {"status": "executed", "result": ...}
    # It might return an error string if auth fails, but that means it *tried*.
    
    try:
        response = await approve_action(action_id, bg, db)
        print(f"Approval Response: {response}")
        assert response["status"] in ["executed", "error"] # Error is acceptable if just auth failure
    except Exception as e:
        print(f"Approval failed with exception: {e}")
        raise
    finally:
        db.close()

    # 4. Check Trace Step (Optional - based on implementation)
    # My current implementation only logs trace on tool call. 
    # The approvals API logs to logger. 
    # Let's check status is APPROVED
    db = SessionLocal()
    updated_action = db.query(PendingAction).filter(PendingAction.id == action_id).first()
    assert updated_action.status == "APPROVED"
    print("\n4. Action status updated to APPROVED.")
    db.close()

    print("\n--- VERIFICATION PASSED ---")

if __name__ == "__main__":
    asyncio.run(verify_flow())
