from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    message = Column(String)
    sender = Column(String) # "user" or "ai"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())