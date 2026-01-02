from sqlalchemy import Column, String, ForeignKey, DateTime, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import enum

from src.database import Base

class OAuthProvider(str, enum.Enum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"

class OAuthAccount(Base):
    __tablename__ = "oauth_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(SQLEnum(OAuthProvider), nullable=False)
    provider_user_id = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False)
    
    # Optional: store tokens if needed for offline access / API calls
    # access_token = Column(String, nullable=True) 
    # refresh_token = Column(String, nullable=True)
    # expires_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", backref="oauth_accounts")

    __table_args__ = (
        # Ensure unique provider_user_id per provider
        # (Though provider_user_id itself is usually globally unique per provider, explicit check helps)
        # UniqueConstraint('provider', 'provider_user_id', name='uq_oauth_provider_uid'),
        {},
    )
