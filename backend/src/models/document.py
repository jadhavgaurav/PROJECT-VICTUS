import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, BigInteger
from sqlalchemy.sql import func
from src.database import Base

class Document(Base):
    """Model for user uploaded documents."""
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    storage_path = Column(String, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
