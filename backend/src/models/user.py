from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from src.database import Base

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
