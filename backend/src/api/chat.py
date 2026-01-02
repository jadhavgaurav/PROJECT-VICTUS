"""
Chat and history endpoints
"""

import os
import traceback
import time
import json
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .. import models
from ..database import get_db, SessionLocal
from ..agent import create_agent_executor
from ..tools import FAISS_INDEX_PATH
from ..utils.context import set_session_id
from ..utils.logging import get_logger
from ..utils.metrics import agent_invocations_total, agent_response_time
from ..auth.dependencies import get_current_user
from .schemas import ChatRequest, HistoryRequest
from ..agent.memory import ConversationContextManager

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["Chat"])


@router.post("/history")
async def get_history(
    request: Request,
    history_request: HistoryRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get chat history for a conversation.
    Ensures user owns the conversation.
    """
    try:
        # Verify ownership
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == history_request.conversation_id,
            models.Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
            
        messages = db.query(models.Message).filter(
            models.Message.conversation_id == history_request.conversation_id
        ).order_by(models.Message.created_at).all()
        
        if not messages:
            return {"history": []}
        
        history_list = [
            {"message": msg.content, "sender": msg.role if msg.role != "assistant" else "ai"}
            for msg in messages
        ]
        return {"history": history_list}
    except HTTPException:
        raise
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
    current_user = Depends(get_current_user)
):
    """
    Handles user chat messages and returns a streaming response.
    Uses Context Optimization (Summarization + Sliding Window).
    """
    start_time = time.time()
    
    try:
        user_id = current_user.id
        conversation_id = chat_request.conversation_id
        
        # Verify ownership
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == conversation_id,
            models.Conversation.user_id == user_id
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Set context variables
        set_session_id(str(user_id))
        
        # Init Context Manager
        context_manager = ConversationContextManager(db, current_user, conversation_id)
        
        # Re-create agent only if RAG status changes (simplified check)
        rag_enabled = os.path.exists(FAISS_INDEX_PATH) and bool(
            os.listdir(FAISS_INDEX_PATH) if os.path.exists(FAISS_INDEX_PATH) else []
        )
        agent_executor = create_agent_executor(rag_enabled=rag_enabled)

        # Get Optimized Context
        system_context_str, chat_history_messages = await context_manager.get_context()
        
        # Inject System Summary if present
        if system_context_str:
            # We prepend a SystemMessage with the summary
            # Note: The agent prompt might already have a System Message. 
            # LangChain handles multiple SystemMessages by concatenating or just listing them.
            chat_history_messages.insert(0, SystemMessage(content=system_context_str))

        # Persist User Message
        try:
            db_user_msg = models.Message(
                user_id=user_id,
                conversation_id=conversation_id,
                role="user",
                content=chat_request.message
            )
            db.add(db_user_msg)
            db.commit()
            logger.info(f"User message saved: {len(chat_request.message)} chars, user_id={user_id}")
        except Exception as db_error:
            logger.error(f"Error saving user message: {db_error}")
            db.rollback()
            # We continue, but this is bad state.
            
        # SSE Generator Function
        async def event_generator():
            final_response_parts = []
            
            # Initial Status
            yield f"event: status\ndata: {{\"phase\": \"thinking\", \"message\": \"Planning response...\"}}\n\n"
            
            try:
                # Use astream_events
                async for event in agent_executor.astream_events(
                    {"input": chat_request.message, "chat_history": chat_history_messages},
                    version="v1"
                ):
                    # Handle Tool Calls
                    if event["event"] == "on_tool_start":
                        tool_name = event["name"]
                        tool_input = event["data"].get("input")
                        
                        yield f"event: status\ndata: {{\"phase\": \"using_tools\", \"message\": \"Using tool: {tool_name}\"}}\n\n"
                        
                        tool_data = json.dumps({
                            "type": "start",
                            "name": tool_name,
                            "input": tool_input
                        })
                        yield f"event: tool\ndata: {tool_data}\n\n"
                        
                    # Handle Tool Output
                    elif event["event"] == "on_tool_end":
                        tool_name = event["name"]
                        tool_output = event["data"].get("output")
                        
                        tool_data = json.dumps({
                            "type": "end",
                            "name": tool_name,
                            "result": str(tool_output)
                        })
                        yield f"event: tool\ndata: {tool_data}\n\n"
                        yield f"event: status\ndata: {{\"phase\": \"thinking\", \"message\": \"Processing tool output...\"}}\n\n"
                    
                    # Handle Stream
                    elif event["event"] == "on_chain_stream":
                        if event["name"] == "AgentExecutor":
                            chunk = event["data"].get("chunk", {})
                            if isinstance(chunk, dict):
                                output = chunk.get("output", "")
                            elif isinstance(chunk, str):
                                output = chunk
                            else:
                                output = str(chunk) if chunk else ""
                            
                            if output:
                                if not final_response_parts:
                                    yield f"event: status\ndata: {{\"phase\": \"synthesizing\", \"message\": \"Generating response...\"}}\n\n"
                                
                                final_response_parts.append(output)
                                token_data = json.dumps({"delta": output})
                                yield f"event: token\ndata: {token_data}\n\n"
                    
                    # Handle Final Output
                    elif event["event"] == "on_chain_end":
                        if event["name"] == "AgentExecutor":
                            output_data = event.get("data", {}).get("output", "")
                            if isinstance(output_data, dict):
                                final_output = output_data.get("output", "")
                            elif isinstance(output_data, str):
                                final_output = output_data
                            else:
                                final_output = str(output_data) if output_data else ""
                            
                            if final_output:
                                existing_text = "".join(final_response_parts)
                                if final_output != existing_text and final_output.startswith(existing_text):
                                    # Stream remaining
                                    remaining = final_output[len(existing_text):]
                                    if remaining:
                                        if not final_response_parts:
                                            yield f"event: status\ndata: {{\"phase\": \"synthesizing\", \"message\": \"Generating response...\"}}\n\n"
                                        final_response_parts.append(remaining)
                                        token_data = json.dumps({"delta": remaining})
                                        yield f"event: token\ndata: {token_data}\n\n"
                                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                logger.error(f"Agent error: {e}", exc_info=True)
                error_data = json.dumps({"message": error_msg, "code": "INTERNAL_ERROR"})
                yield f"event: error\ndata: {error_data}\n\n"

            # Persist AI Message
            final_response = "".join(final_response_parts).strip()
            if final_response:
                try:
                    fresh_db = SessionLocal()
                    try:
                        db_ai_msg = models.Message(
                            user_id=user_id,
                            conversation_id=conversation_id,
                            role="assistant",
                            content=final_response
                        )
                        fresh_db.add(db_ai_msg)
                        fresh_db.commit()
                    finally:
                        fresh_db.close()
                except Exception as db_error:
                    logger.error(f"Error saving AI message: {db_error}")
            
            yield f"event: done\ndata: {{\"ok\": true}}\n\n"

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
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred"
        )
