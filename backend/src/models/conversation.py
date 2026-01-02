import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from src.database import Base

class Conversation(Base):
    """Model for a chat conversation."""
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    title = Column(String, nullable=False, default="New Conversation")
    pinned = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class Message(Base):
    """Model for a message in a conversation."""
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    role = Column(String, nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=False)
    
    token_count = Column(Integer, nullable=True)
    metadata_json = Column(JSON, nullable=True)  # citations, tool_calls, etc
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ConversationMemory(Base):
    """Model for persistent summarization of a conversation."""
    __tablename__ = "conversation_memories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    summary_text = Column(Text, nullable=True)
    summary_version = Column(Integer, default=0)
    
    summarized_until_message_id = Column(String, nullable=True) # UUID of the last summarized message
    summarized_until_created_at = Column(DateTime(timezone=True), nullable=True)
    
    last_summary_token_estimate = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserFact(Base):
    """Model for storing user facts (long-term memory). Copied from legacy."""
    __tablename__ = "user_facts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Can be user ID (int as string) or session_id
    key = Column(String, index=True)
    value = Column(String)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
