from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, Integer
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from src.database import Base

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="reset_tokens")
