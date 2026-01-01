"""
Database models for Project VICTUS
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    """Model for storing user accounts."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    provider = Column(String, default="local")  # local, google, microsoft
    provider_id = Column(String, nullable=True)  # OAuth provider user ID
    avatar_url = Column(String, nullable=True)
    # Microsoft OAuth tokens for M365 tools (encrypted in production)
    microsoft_access_token = Column(String, nullable=True)
    microsoft_refresh_token = Column(String, nullable=True)
    microsoft_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

class ChatMessage(Base):
    """Model for storing chat messages."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)  # Link to user
    session_id = Column(String, index=True)
    message = Column(String)
    sender = Column(String)  # "user" or "ai"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class UserFact(Base):
    """Model for storing user facts (long-term memory)."""
    __tablename__ = "user_facts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Can be user ID (int as string) or session_id
    key = Column(String, index=True)
    value = Column(String)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

