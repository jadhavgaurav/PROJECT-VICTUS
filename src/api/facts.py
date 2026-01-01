"""
Facts/Memory management endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import UserFact, User
from ..auth.dependencies import get_optional_user
from ..utils.logging import get_logger
from ..utils.context import get_user_id
from .schemas import (
    FactsResponse, FactItem, FactCreate, FactUpdate,
    FactsImport, FactsImportResponse
)

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Facts"])


def get_user_identifier(current_user: Optional[User]) -> str:
    """Get user identifier for facts (user_id or session_id)."""
    if current_user:
        return str(current_user.id)
    # For unauthenticated users, use session_id from context
    return get_user_id()


@router.get("/facts", response_model=FactsResponse)
async def get_facts(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user),
    limit: int = 100,
    offset: int = 0,
    search: Optional[str] = None
):
    """
    Get all facts for the current user.
    Supports search by key or value.
    """
    try:
        user_id = get_user_identifier(current_user)
        
        query = db.query(UserFact).filter(UserFact.user_id == user_id)
        
        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (UserFact.key.like(search_term)) |
                (UserFact.value.like(search_term))
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination and ordering
        facts = query.order_by(UserFact.last_updated.desc()).offset(offset).limit(limit).all()
        
        fact_items = [
            FactItem(
                id=fact.id,
                key=fact.key,
                value=fact.value,
                last_updated=fact.last_updated.isoformat()
            )
            for fact in facts
        ]
        
        return FactsResponse(facts=fact_items, total=total)
    except Exception as e:
        logger.error(f"Error getting facts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving facts"
        )


@router.post("/facts", response_model=FactItem, status_code=status.HTTP_201_CREATED)
async def create_fact(
    fact_data: FactCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Create a new fact.
    """
    try:
        user_id = get_user_identifier(current_user)
        
        # Check if fact with same key already exists
        existing = db.query(UserFact).filter(
            UserFact.user_id == user_id,
            UserFact.key == fact_data.key
        ).first()
        
        if existing:
            # Update existing fact
            existing.value = fact_data.value
            db.commit()
            db.refresh(existing)
            logger.info(f"Updated fact '{fact_data.key}' for user {user_id}")
            
            return FactItem(
                id=existing.id,
                key=existing.key,
                value=existing.value,
                last_updated=existing.last_updated.isoformat()
            )
        
        # Create new fact
        new_fact = UserFact(
            user_id=user_id,
            key=fact_data.key,
            value=fact_data.value
        )
        db.add(new_fact)
        db.commit()
        db.refresh(new_fact)
        
        logger.info(f"Created fact '{fact_data.key}' for user {user_id}")
        
        return FactItem(
            id=new_fact.id,
            key=new_fact.key,
            value=new_fact.value,
            last_updated=new_fact.last_updated.isoformat()
        )
    except Exception as e:
        logger.error(f"Error creating fact: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating fact"
        )


@router.put("/facts/{fact_id}", response_model=FactItem)
async def update_fact(
    fact_id: int,
    fact_data: FactUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Update an existing fact.
    """
    try:
        user_id = get_user_identifier(current_user)
        
        fact = db.query(UserFact).filter(
            UserFact.id == fact_id,
            UserFact.user_id == user_id
        ).first()
        
        if not fact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fact not found"
            )
        
        # Update fields if provided
        if fact_data.key is not None:
            fact.key = fact_data.key
        if fact_data.value is not None:
            fact.value = fact_data.value
        
        db.commit()
        db.refresh(fact)
        
        logger.info(f"Updated fact {fact_id} for user {user_id}")
        
        return FactItem(
            id=fact.id,
            key=fact.key,
            value=fact.value,
            last_updated=fact.last_updated.isoformat()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating fact: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating fact"
        )


@router.delete("/facts/{fact_id}")
async def delete_fact(
    fact_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Delete a fact.
    """
    try:
        user_id = get_user_identifier(current_user)
        
        fact = db.query(UserFact).filter(
            UserFact.id == fact_id,
            UserFact.user_id == user_id
        ).first()
        
        if not fact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fact not found"
            )
        
        db.delete(fact)
        db.commit()
        
        logger.info(f"Deleted fact {fact_id} for user {user_id}")
        
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting fact: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting fact"
        )


@router.get("/facts/export")
async def export_facts(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Export all facts as JSON.
    """
    try:
        user_id = get_user_identifier(current_user)
        
        facts = db.query(UserFact).filter(
            UserFact.user_id == user_id
        ).all()
        
        facts_data = [
            {"key": fact.key, "value": fact.value}
            for fact in facts
        ]
        
        from fastapi.responses import JSONResponse
        return JSONResponse(content={
            "user_id": user_id,
            "total": len(facts_data),
            "facts": facts_data
        })
    except Exception as e:
        logger.error(f"Error exporting facts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting facts"
        )


@router.post("/facts/import", response_model=FactsImportResponse)
async def import_facts(
    import_data: FactsImport,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Import facts from JSON.
    """
    try:
        user_id = get_user_identifier(current_user)
        imported = 0
        failed = 0
        errors = []
        
        for fact_data in import_data.facts:
            try:
                if not isinstance(fact_data, dict) or "key" not in fact_data or "value" not in fact_data:
                    failed += 1
                    errors.append(f"Invalid fact format: {fact_data}")
                    continue
                
                key = str(fact_data["key"])
                value = str(fact_data["value"])
                
                # Check if exists
                existing = db.query(UserFact).filter(
                    UserFact.user_id == user_id,
                    UserFact.key == key
                ).first()
                
                if existing:
                    existing.value = value
                else:
                    new_fact = UserFact(
                        user_id=user_id,
                        key=key,
                        value=value
                    )
                    db.add(new_fact)
                
                imported += 1
            except Exception as e:
                failed += 1
                errors.append(f"Error importing fact {fact_data}: {str(e)}")
        
        db.commit()
        
        logger.info(f"Imported {imported} facts for user {user_id}, {failed} failed")
        
        return FactsImportResponse(
            imported=imported,
            failed=failed,
            errors=errors[:10]  # Limit errors to first 10
        )
    except Exception as e:
        logger.error(f"Error importing facts: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error importing facts"
        )

