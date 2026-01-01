"""
Conversation management endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ChatMessage, User
from ..auth.dependencies import get_optional_user
from ..utils.logging import get_logger
from .schemas import ConversationsResponse, ConversationItem, ConversationTitleUpdate

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Conversations"])


@router.get("/conversations", response_model=ConversationsResponse)
async def get_conversations(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
    limit: int = 100,
    offset: int = 0
):
    """
    Get all conversations for the current user.
    Returns list of conversations with metadata.
    """
    try:
        # Build query based on authentication
        if current_user:
            # Authenticated users: get conversations by user_id
            query = db.query(
                ChatMessage.session_id,
                func.max(ChatMessage.timestamp).label('last_activity'),
                func.min(ChatMessage.timestamp).label('created_at'),
                func.count(ChatMessage.id).label('message_count'),
                func.max(ChatMessage.message).label('last_message')
            ).filter(
                ChatMessage.user_id == current_user.id
            ).group_by(ChatMessage.session_id)
        else:
            # Unauthenticated users: get conversations by session_id without user_id
            query = db.query(
                ChatMessage.session_id,
                func.max(ChatMessage.timestamp).label('last_activity'),
                func.min(ChatMessage.timestamp).label('created_at'),
                func.count(ChatMessage.id).label('message_count'),
                func.max(ChatMessage.message).label('last_message')
            ).filter(
                ChatMessage.user_id.is_(None)
            ).group_by(ChatMessage.session_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        conversations = query.order_by(
            func.max(ChatMessage.timestamp).desc()
        ).offset(offset).limit(limit).all()
        
        # Format response
        conversation_items = []
        for conv in conversations:
            # Generate title from first message (truncated)
            title = None
            if conv.last_message:
                title = conv.last_message[:50] + "..." if len(conv.last_message) > 50 else conv.last_message
            
            conversation_items.append(ConversationItem(
                session_id=conv.session_id,
                title=title,
                last_message=conv.last_message[:100] + "..." if conv.last_message and len(conv.last_message) > 100 else conv.last_message,
                timestamp=conv.last_activity.isoformat() if conv.last_activity else "",
                message_count=conv.message_count,
                created_at=conv.created_at.isoformat() if conv.created_at else None
            ))
        
        return ConversationsResponse(
            conversations=conversation_items,
            total=total
        )
    except Exception as e:
        logger.error(f"Error getting conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving conversations"
        )


@router.delete("/conversations/{session_id}")
async def delete_conversation(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Delete a conversation and all its messages.
    """
    try:
        # Build query based on authentication
        query = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)
        
        if current_user:
            # Authenticated users: only delete their own conversations
            query = query.filter(ChatMessage.user_id == current_user.id)
        else:
            # Unauthenticated users: only delete conversations without user_id
            query = query.filter(ChatMessage.user_id.is_(None))
        
        messages = query.all()
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Delete all messages
        for message in messages:
            db.delete(message)
        
        db.commit()
        logger.info(f"Deleted conversation {session_id} with {len(messages)} messages")
        
        return {"status": "success", "deleted_messages": len(messages)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting conversation"
        )


@router.put("/conversations/{session_id}/title")
async def update_conversation_title(
    session_id: str,
    title_update: ConversationTitleUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Update conversation title.
    Note: Currently, titles are generated from first message.
    This endpoint stores the title preference (could be stored in a separate table in future).
    For now, it just validates the request.
    """
    try:
        # Verify conversation exists
        query = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)
        
        if current_user:
            query = query.filter(ChatMessage.user_id == current_user.id)
        else:
            query = query.filter(ChatMessage.user_id.is_(None))
        
        if not query.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # TODO: Store title in a separate Conversation model if needed
        # For now, just return success
        return {
            "status": "success",
            "session_id": session_id,
            "title": title_update.title
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating conversation title: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating conversation title"
        )


@router.get("/conversations/{session_id}/export")
async def export_conversation(
    session_id: str,
    format: str = "json",
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Export a conversation in various formats.
    Formats: json, markdown
    """
    try:
        # Build query
        query = db.query(ChatMessage).filter(ChatMessage.session_id == session_id)
        
        if current_user:
            query = query.filter(ChatMessage.user_id == current_user.id)
        else:
            query = query.filter(ChatMessage.user_id.is_(None))
        
        messages = query.order_by(ChatMessage.timestamp).all()
        
        if not messages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Format messages
        formatted_messages = [
            {
                "sender": msg.sender,
                "message": msg.message,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in messages
        ]
        
        if format == "json":
            from fastapi.responses import JSONResponse
            return JSONResponse(content={
                "session_id": session_id,
                "exported_at": messages[-1].timestamp.isoformat() if messages else "",
                "message_count": len(messages),
                "messages": formatted_messages
            })
        elif format == "markdown":
            from fastapi.responses import Response
            markdown_content = f"# Conversation Export\n\n"
            markdown_content += f"**Session ID:** {session_id}\n"
            markdown_content += f"**Messages:** {len(messages)}\n\n"
            markdown_content += "---\n\n"
            
            for msg in formatted_messages:
                sender_label = "**You**" if msg["sender"] == "user" else "**VICTUS**"
                markdown_content += f"{sender_label} ({msg['timestamp']})\n\n"
                markdown_content += f"{msg['message']}\n\n"
                markdown_content += "---\n\n"
            
            return Response(
                content=markdown_content,
                media_type="text/markdown",
                headers={"Content-Disposition": f'attachment; filename="conversation_{session_id}.md"'}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid format. Supported: json, markdown"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting conversation"
        )

