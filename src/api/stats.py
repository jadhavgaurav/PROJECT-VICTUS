"""
Usage statistics endpoints
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
import os

from ..database import get_db
from ..models import ChatMessage, UserFact, User
from ..auth.dependencies import get_optional_user
from ..utils.logging import get_logger
from .schemas import UsageStatsResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Stats"])


@router.get("/stats", response_model=UsageStatsResponse)
async def get_usage_stats(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get usage statistics for the current user.
    """
    try:
        if current_user:
            user_id = current_user.id
            user_id_str = str(user_id)
        else:
            # For unauthenticated users, we can't provide accurate stats
            # Return basic stats based on session
            return UsageStatsResponse(
                total_messages=0,
                total_conversations=0,
                documents_uploaded=0,
                facts_stored=0,
                api_calls=None,
                usage_by_date=[]
            )
        
        # Get message count
        message_count = db.query(func.count(ChatMessage.id)).filter(
            ChatMessage.user_id == user_id
        ).scalar() or 0
        
        # Get conversation count (unique session_ids)
        conversation_count = db.query(func.count(func.distinct(ChatMessage.session_id))).filter(
            ChatMessage.user_id == user_id
        ).scalar() or 0
        
        # Get facts count
        facts_count = db.query(func.count(UserFact.id)).filter(
            UserFact.user_id == user_id_str
        ).scalar() or 0
        
        # Get documents count
        upload_dir = "uploads"
        documents_count = 0
        if os.path.exists(upload_dir):
            documents_count = len([
                f for f in os.listdir(upload_dir)
                if f.endswith(".pdf") or f.endswith(".docx")
            ])
        
        # Get usage by date (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        usage_by_date = []
        
        daily_stats = db.query(
            func.date(ChatMessage.timestamp).label('date'),
            func.count(ChatMessage.id).label('count')
        ).filter(
            ChatMessage.user_id == user_id,
            ChatMessage.timestamp >= thirty_days_ago
        ).group_by(
            func.date(ChatMessage.timestamp)
        ).order_by(
            func.date(ChatMessage.timestamp)
        ).all()
        
        for stat in daily_stats:
            usage_by_date.append({
                "date": stat.date.isoformat() if hasattr(stat.date, 'isoformat') else str(stat.date),
                "count": stat.count
            })
        
        return UsageStatsResponse(
            total_messages=message_count,
            total_conversations=conversation_count,
            documents_uploaded=documents_count,
            facts_stored=facts_count,
            api_calls=None,  # Could be tracked separately if needed
            usage_by_date=usage_by_date
        )
    except Exception as e:
        logger.error(f"Error getting usage stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving usage statistics"
        )

