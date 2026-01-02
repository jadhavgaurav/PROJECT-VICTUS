from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from ..database import get_db
from ..models import User, Conversation, Message
from ..auth.dependencies import get_current_user
from ..utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])

# Pydantic Models
class ConversationCreate(BaseModel):
    title: str = "New Chat"

class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    pinned: Optional[bool] = None
    archived: Optional[bool] = None

class ConversationOut(BaseModel):
    id: str
    title: str
    pinned: bool
    archived: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    metadata_json: Optional[dict] = None
    
    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[ConversationOut])
async def get_conversations(
    limit: int = 50,
    skip: int = 0,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's conversations."""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user.id,
        Conversation.deleted_at.is_(None)
    ).order_by(desc(Conversation.updated_at)).offset(skip).limit(limit).all()
    
    return conversations

@router.post("", response_model=ConversationOut)
async def create_conversation(
    data: ConversationCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new conversation."""
    new_conv = Conversation(
        user_id=user.id,
        title=data.title
    )
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)
    return new_conv

@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation details."""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
        Conversation.deleted_at.is_(None)
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    return conv

@router.patch("/{conversation_id}", response_model=ConversationOut)
async def update_conversation(
    conversation_id: str,
    data: ConversationUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update conversation (title, pin, archive)."""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
        Conversation.deleted_at.is_(None)
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    if data.title is not None:
        conv.title = data.title
    if data.pinned is not None:
        conv.pinned = data.pinned
    if data.archived is not None:
        conv.archived = data.archived
        
    db.commit()
    db.refresh(conv)
    return conv

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete conversation."""
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id,
        Conversation.deleted_at.is_(None)
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
        
    conv.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Conversation deleted"}

@router.get("/{conversation_id}/messages", response_model=List[MessageOut])
async def get_messages(
    conversation_id: str,
    limit: int = 50,
    before: Optional[str] = None, # pagination cursor?
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for conversation."""
    # Ensure user owns conversation
    conv = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()
    
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    query = db.query(Message).filter(
        Message.conversation_id == conversation_id
    )
    
    if before:
        # If using ID based cursor, ideally we have a reliable sort order
        pass 
        
    messages = query.order_by(Message.created_at.asc()).all()
    # Note: Pagination would be better, but for now retrieving all or limit
    
    return messages
