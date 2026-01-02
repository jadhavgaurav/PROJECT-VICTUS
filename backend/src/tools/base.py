import uuid
import json
import inspect
import time
from enum import Enum
from typing import Optional, Type, Any, Callable
from pydantic import BaseModel
from langchain_core.tools import BaseTool

from langchain_core.tools import BaseTool

from ..database import SessionLocal
from ..models import PendingAction, TraceStep
from ..utils.context import get_trace_id, get_user_id

class RiskLevel(str, Enum):
    LOW = "low"         # Read-only, safe
    MEDIUM = "medium"   # Writes without external side effects or minor impact
    HIGH = "high"       # Significant side effects

class SafeTool(BaseTool):
    """
    A wrapper around LangChain's BaseTool that adds a risk_level 
    and policy enforcement capability.
    """
    risk_level: RiskLevel = RiskLevel.HIGH
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    @classmethod
    def from_func(
        cls,
        func: Callable,
        name: str,
        description: str,
        args_schema: Type[BaseModel],
        risk_level: RiskLevel = RiskLevel.HIGH,
        return_direct: bool = False,
    ) -> "SafeTool":
        """
        Creates a SafeTool from a function.
        """
        instance = cls(
            name=name,
            description=description,
            args_schema=args_schema,
            risk_level=risk_level,
            return_direct=return_direct,
        )
        object.__setattr__(instance, "_func", func)
        return instance

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        # Check Policy
        from ..policy.engine import policy_engine, PolicyDecision
        decision = policy_engine.check_permission(
            tool_name=self.name,
            risk_level=self.risk_level,
            args=kwargs,
            user_id=get_user_id()
        )

        trace_id = get_trace_id()
        start_time = time.time()
        
        # Log Trace Step (Initial)
        if trace_id:
            self._log_trace_step(trace_id, decision, kwargs, result=None, duration=0)

        if decision == PolicyDecision.DENY:
            return f"Action Denied: You do not have permission to execute '{self.name}'."
        
        if decision == PolicyDecision.REQUIRE_APPROVAL:
            # Create Pending Action
            action_id = str(uuid.uuid4())
            self._create_pending_action(action_id, kwargs)
            return (
                f"Action Requires Approval (ID: {action_id}). "
                f"I have created a request to {self.name} with these arguments. "
                "Please approve it in the dashboard to proceed."
            )

        # Execute
        try:
            if hasattr(self, "_func"):
                result = self._func(*args, **kwargs)
            else:
                raise NotImplementedError("Tool function not implemented")
            
            # Log Trace Step (Update with result) - Optional or just rely on completion log
            # For simplicity, we assume success.
            # In a real system, we'd update the TraceStep record.
            return result
            
        except Exception as e:
            return f"Error executing {self.name}: {e}"

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # Async version with same logic
        from ..policy.engine import policy_engine, PolicyDecision
        decision = policy_engine.check_permission(
            tool_name=self.name,
            risk_level=self.risk_level,
            args=kwargs,
            user_id=get_user_id()
        )
        
        if decision == PolicyDecision.DENY:
            return f"Action Denied: You do not have permission to execute '{self.name}'."
        
        if decision == PolicyDecision.REQUIRE_APPROVAL:
             action_id = str(uuid.uuid4())
             self._create_pending_action(action_id, kwargs)
             return (
                f"Action Requires Approval (ID: {action_id}). "
                "Please approve it in the dashboard to proceed."
            )

        if hasattr(self, "_func"):
             if inspect.iscoroutinefunction(self._func):
                 return await self._func(*args, **kwargs)
             return self._func(*args, **kwargs)
        raise NotImplementedError("Tool function not implemented")

    def _create_pending_action(self, action_id: str, args: dict):
        db = SessionLocal()
        try:
            action = PendingAction(
                id=action_id,
                tool_name=self.name,
                risk_level=self.risk_level.value,
                args=json.dumps(args),
                status="PENDING"
            )
            db.add(action)
            db.commit()
        except Exception as e:
            db.rollback()
            # Log error
            print(f"Error creating pending action: {e}")
        finally:
            db.close()

    def _log_trace_step(self, trace_id: str, decision: str, args: dict, result: Any, duration: float):
        # Basic fire-and-forget logging
        db = SessionLocal()
        try:
            step = TraceStep(
                trace_id=trace_id,
                tool_name=self.name,
                args=json.dumps(args),
                decision=decision.value,
                output=str(result)[:500] if result else None, # Truncate large outputs
                duration_ms=int(duration * 1000)
            )
            db.add(step)
            db.commit()
        except Exception:
            pass # Don't block on logging fail
        finally:
            db.close()
