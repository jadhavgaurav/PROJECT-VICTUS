from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from src.database import Base

class Trace(Base):
    """Model for storing execution traces."""
    __tablename__ = "traces"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    user_id = Column(String, index=True, nullable=True)
    conversation_id = Column(String, index=True, nullable=True) # Added
    input_text = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TraceStep(Base):
    """Model for storing individual steps within a trace."""
    __tablename__ = "trace_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String, index=True, nullable=False)
    tool_name = Column(String, nullable=False)
    args = Column(String, nullable=True)
    decision = Column(String, nullable=False)  # ALLOW, DENY, APPROVED
    output = Column(String, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class PendingAction(Base):
    """Model for storing actions that require human approval."""
    __tablename__ = "pending_actions"
    
    id = Column(String, primary_key=True, index=True)  # UUID
    user_id = Column(Integer, index=True, nullable=True) # Added to link to user
    conversation_id = Column(String, index=True, nullable=True) # Added
    
    tool_name = Column(String, nullable=False)
    risk_level = Column(String, nullable=False)
    args = Column(String, nullable=False)  # JSON string of arguments
    status = Column(String, default="PENDING", index=True)  # PENDING, APPROVED, DENIED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
