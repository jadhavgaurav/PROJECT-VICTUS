"""
Chat and history endpoints
"""

import os
import traceback
import time
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage

from .. import models
from ..database import get_db, SessionLocal
from ..agent import create_agent_executor
from ..tools import FAISS_INDEX_PATH
from ..utils.context import set_session_id
from ..utils.logging import get_logger
from ..utils.metrics import agent_invocations_total, agent_response_time
from ..auth.dependencies import get_optional_user
from .schemas import ChatRequest, HistoryRequest

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/history")
async def get_history(
    request: Request,
    history_request: HistoryRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """Get chat history for a session, filtered by user if authenticated."""
    try:
        # Build query - filter by user_id if authenticated, otherwise by session_id
        query = db.query(models.ChatMessage)
        
        if current_user:
            # Authenticated users: filter by user_id AND session_id
            query = query.filter(
                models.ChatMessage.user_id == current_user.id,
                models.ChatMessage.session_id == history_request.session_id
            )
        else:
            # Unauthenticated users: filter only by session_id
            query = query.filter(
                models.ChatMessage.session_id == history_request.session_id,
                models.ChatMessage.user_id.is_(None)  # Only show messages without user_id
            )
        
        history = query.order_by(models.ChatMessage.timestamp).all()
        
        if not history:
            welcome_message = {
                "message": "Hello! I'm VICTUS, your personal AI assistant. How can I help you today?",
                "sender": "ai"
            }
            return {"history": [welcome_message]}
        
        history_list = [
            {"message": msg.message, "sender": msg.sender}
            for msg in history
        ]
        return {"history": history_list}
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving chat history"
        )


@router.post("/chat")
async def chat_endpoint(
    request: Request,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_optional_user)
):
    """
    Handles user chat messages and returns a streaming response (SSE) for real-time updates
    on LLM output and tool execution.
    
    **Example Request:**
    ```json
    {
        "message": "What's the weather in Mumbai?",
        "session_id": "session_12345"
    }
    ```
    
    **Response:**
    Server-Sent Events (SSE) stream with:
    - `EVENT_TOOL_START`: Tool execution started
    - `EVENT_TOOL_END`: Tool execution completed
    - `OUTPUT_STREAM`: AI response chunks
    - `STREAM_END`: Stream completed
    - `ERROR`: Error occurred
    """
    start_time = time.time()
    
    try:
        # Extract user_id BEFORE async generator (to avoid session issues)
        user_id = current_user.id if current_user else None
        
        # Set session context for tools (use user_id if authenticated, otherwise session_id)
        if current_user:
            set_session_id(str(current_user.id))
        else:
            set_session_id(chat_request.session_id)
        
        # Re-create agent only if RAG status changes
        rag_enabled = os.path.exists(FAISS_INDEX_PATH) and bool(
            os.listdir(FAISS_INDEX_PATH) if os.path.exists(FAISS_INDEX_PATH) else []
        )
        agent_executor = create_agent_executor(rag_enabled=rag_enabled)

        # Setup History - filter by user_id if authenticated, otherwise by session_id
        history_query = db.query(models.ChatMessage).filter(
            models.ChatMessage.session_id == chat_request.session_id
        )
        
        if current_user:
            # Authenticated users: only see their own messages
            history_query = history_query.filter(models.ChatMessage.user_id == current_user.id)
        else:
            # Unauthenticated users: only see messages without user_id
            history_query = history_query.filter(models.ChatMessage.user_id.is_(None))
        
        history = history_query.order_by(models.ChatMessage.timestamp).all()
        
        chat_history_messages = [
            HumanMessage(content=msg.message) if msg.sender == "user"
            else AIMessage(content=msg.message)
            for msg in history
        ]

        # Persist User Message
        try:
            db_user_msg = models.ChatMessage(
                user_id=user_id,
                session_id=chat_request.session_id,
                message=chat_request.message,
                sender="user"
            )
            db.add(db_user_msg)
            db.commit()
            logger.info(f"User message saved: {len(chat_request.message)} chars, user_id={user_id}")
        except Exception as db_error:
            logger.error(f"Error saving user message to database: {db_error}")
            db.rollback()
            # Continue even if DB save fails

        # SSE Generator Function
        async def event_generator():
            final_response_parts = []
            try:
                # Use astream_events for real-time tool execution visibility
                async for event in agent_executor.astream_events(
                    {"input": chat_request.message, "chat_history": chat_history_messages},
                    version="v1"
                ):
                    # Handle Tool Calls (Intermediate Steps)
                    if event["event"] == "on_tool_start":
                        tool_name = event["name"]
                        tool_input = event["data"].get("input")
                        stream_data = f"EVENT_TOOL_START:{tool_name}|{tool_input}"
                        yield f"data: {stream_data}\n\n"
                        
                    # Handle Tool Output (Intermediate Steps)
                    elif event["event"] == "on_tool_end":
                        tool_name = event["name"]
                        stream_data = f"EVENT_TOOL_END:{tool_name}"
                        yield f"data: {stream_data}\n\n"
                    
                    # Handle final LLM output streaming chunk by chunk
                    elif event["event"] == "on_chain_stream":
                        if event["name"] == "AgentExecutor":
                            chunk = event["data"].get("chunk", {})
                            # Handle different chunk formats
                            if isinstance(chunk, dict):
                                output = chunk.get("output", "")
                            elif isinstance(chunk, str):
                                output = chunk
                            else:
                                output = str(chunk) if chunk else ""
                            
                            if output:
                                final_response_parts.append(output)
                                stream_data = f"OUTPUT_STREAM:{output}"
                                yield f"data: {stream_data}\n\n"
                    
                    # Handle final output from on_chain_end
                    elif event["event"] == "on_chain_end":
                        if event["name"] == "AgentExecutor":
                            output_data = event.get("data", {}).get("output", "")
                            # Output might be a dict with 'output' key or a string
                            if isinstance(output_data, dict):
                                final_output = output_data.get("output", "")
                            elif isinstance(output_data, str):
                                final_output = output_data
                            else:
                                final_output = str(output_data) if output_data else ""
                            
                            if final_output:
                                # Check if we already have this output
                                existing_text = "".join(final_response_parts)
                                if final_output not in existing_text:
                                    # Only stream the remaining part
                                    remaining = final_output[len(existing_text):]
                                    if remaining:
                                        final_response_parts.append(remaining)
                                        stream_data = f"OUTPUT_STREAM:{remaining}"
                                        yield f"data: {stream_data}\n\n"
                                
            except Exception as e:
                error_msg = f"An unexpected error occurred: {e}"
                logger.error("--- AGENT INVOCATION ERROR ---")
                logger.error(traceback.format_exc())
                yield f"data: ERROR:{error_msg}\n\n"

            # After Streaming, Persist Final Message
            final_response = "".join(final_response_parts).strip()
            if final_response:
                try:
                    # Use a fresh database session for saving (avoid session closure issues)
                    fresh_db = SessionLocal()
                    try:
                        db_ai_msg = models.ChatMessage(
                            user_id=user_id,  # Use captured user_id from outer scope
                            session_id=chat_request.session_id,
                            message=final_response,
                            sender="ai"
                        )
                        fresh_db.add(db_ai_msg)
                        fresh_db.commit()
                        logger.info(f"AI message saved: {len(final_response)} chars, user_id={user_id}")
                    finally:
                        fresh_db.close()
                except Exception as db_error:
                    logger.error(f"Error saving AI message to database: {db_error}")
                    logger.error(traceback.format_exc())
                    # Don't fail the request if DB save fails
            else:
                logger.warning("No final response to save (empty response)")
                
            # Send an explicit stream termination signal
            yield "data: STREAM_END\n\n"

        response_time = time.time() - start_time
        agent_response_time.observe(response_time)
        agent_invocations_total.labels(status="success").inc()
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except HTTPException:
        agent_invocations_total.labels(status="error").inc()
        raise
    except Exception as e:
        agent_invocations_total.labels(status="error").inc()
        logger.error(f"Error in chat endpoint: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )

