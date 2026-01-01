"""
Long-term memory tools for storing and recalling user facts
"""

from sqlalchemy.orm import Session
from langchain_core.tools import tool

from ..database import SessionLocal
from ..models import UserFact
from ..utils.context import get_user_id

@tool
def remember_fact(key: str, value: str, user_id: str = None) -> str:
    """
    Stores a key-value pair as a personal fact for long-term memory. 
    Use this to remember names, preferences, or important dates.
    For example, key='wife\'s name', value='Jane'.
    
    Note: If user_id is not provided, it will use the current session context.
    """
    if not user_id:
        user_id = get_user_id()
    
    db: Session = SessionLocal()
    try:
        # Check if fact exists (user_id + key should be unique per user)
        fact = db.query(UserFact).filter(
            UserFact.user_id == str(user_id),
            UserFact.key == key
        ).first()
        if fact:
            fact.value = value
            db.commit()
            return f"Updated fact '{key}' to '{value}'."
        else:
            new_fact = UserFact(user_id=str(user_id), key=key, value=value)
            db.add(new_fact)
            db.commit()
            return f"Remembered new fact: '{key}' set to '{value}'."
    except Exception as e:
        db.rollback()
        return f"Error remembering fact: {e}"
    finally:
        db.close()

@tool
def recall_fact(key: str, user_id: str = None) -> str:
    """
    Recalls a specific personal fact previously stored in long-term memory by its key.
    Returns the stored value or a 'not found' message.
    
    Note: If user_id is not provided, it will use the current session context.
    """
    if not user_id:
        user_id = get_user_id()
    
    db: Session = SessionLocal()
    try:
        fact = db.query(UserFact).filter(
            UserFact.user_id == str(user_id),
            UserFact.key == key
        ).first()
        if fact:
            return f"The stored fact for '{key}' is: '{fact.value}'"
        else:
            return f"Fact not found. I don't have a stored fact for '{key}'."
    except Exception as e:
        return f"Error recalling fact: {e}"
    finally:
        db.close()

