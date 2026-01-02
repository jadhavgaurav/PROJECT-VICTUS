from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..models import Conversation, Message, ConversationMemory, User
from ..config import settings
from ..utils.logging import get_logger

logger = get_logger(__name__)

# Configuration
RECENT_MESSAGES_WINDOW = 12
SUMMARY_TRIGGER_MESSAGES = 8

class ConversationContextManager:
    """
    Manages conversation context, including summarization and history retrieval.
    """
    
    def __init__(self, db: Session, user: User, conversation_id: str):
        self.db = db
        self.user = user
        self.conversation_id = conversation_id
        
        # Initialize summarizer LLM (cheaper model for summarization)
        self.summarizer_llm = ChatOpenAI(
            model="gpt-4o-mini", # Use mini/turbo for summarization
            temperature=0,
            openai_api_key=settings.OPENAI_API_KEY
        )

    async def get_context(self) -> Tuple[SystemMessage, List[BaseMessage]]:
        """
        Builds the context for the agent:
        1. Checks if summarization is needed and updates memory.
        2. Retrieves the summary.
        3. Retrieves recent messages.
        4. Constructs the System Message with Summary.
        5. Returns System Message + Recent Messages.
        """
        
        # 1. Update summary if needed
        await self._update_summary_if_needed()
        
        # 2. Fetch Memory
        memory = self.db.query(ConversationMemory).filter(
            ConversationMemory.conversation_id == self.conversation_id
        ).first()
        
        summary_text = memory.summary_text if memory and memory.summary_text else ""
        
        # 3. Fetch Recent Messages
        # We want the last N messages
        # But we need to make sure we don't fetch messages that were already summarized
        # UNLESS we are using a sliding window where we ALWAYS show the last N, 
        # even if they are part of the summary (for continuity).
        # Strategy: Always show last RECENT_MESSAGES_WINDOW messages verbatim.
        # The summary covers everything BEFORE that window.
        
        # Get total count
        total_count = self.db.query(Message).filter(
            Message.conversation_id == self.conversation_id
        ).count()
        
        skip = max(0, total_count - RECENT_MESSAGES_WINDOW)
        
        recent_db_messages = self.db.query(Message).filter(
            Message.conversation_id == self.conversation_id
        ).order_by(asc(Message.created_at)).offset(skip).all()
        
        # Convert to LangChain messages
        chat_history: List[BaseMessage] = []
        for msg in recent_db_messages:
            if msg.role == "user":
                chat_history.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant" or msg.role == "ai":
                chat_history.append(AIMessage(content=msg.content))
            # System/Tool messages handling if needed
            
        # 4. Construct System Message Supplement
        # The base system prompt is in agent.py. 
        # We can prepend the summary to the history or strictly as a SystemMessage.
        # Actually, AgentExecutor expects chat_history. 
        # We will return the summary string to be injected into the prompt, 
        # OR we insert a SystemMessage with the summary at the start of chat_history.
        
        system_context = ""
        if summary_text:
            system_context = f"## Previous Conversation Summary\n{summary_text}\n\n"
            
        return system_context, chat_history

    async def _update_summary_if_needed(self):
        """
        Checks if we have enough unsummarized messages to trigger an update.
        """
        # Get or Create Memory Record
        memory = self.db.query(ConversationMemory).filter(
            ConversationMemory.conversation_id == self.conversation_id
        ).first()
        
        if not memory:
            memory = ConversationMemory(
                conversation_id=self.conversation_id,
                user_id=self.user.id,
                summary_text=""
            )
            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)
            
        # Find messages since last summary
        query = self.db.query(Message).filter(
            Message.conversation_id == self.conversation_id
        )
        
        if memory.summarized_until_message_id:
             # Find the timestamp of the last summarized message to be safe
             last_msg = self.db.query(Message).filter(Message.id == memory.summarized_until_message_id).first()
             if last_msg:
                 query = query.filter(Message.created_at > last_msg.created_at)
        
        unsummarized_messages = query.order_by(asc(Message.created_at)).all()
        
        # We only summarize if we have enough new messages AND 
        # we leave the recent window alone (i.e. we summarize messages that have fallen out of the window)
        # But for simplicity, the prompt says: "update summary every 8 new messages beyond summarized_until".
        # And "Messages older than N, include Summary".
        
        # Let's say we have 20 messages. Window is 12.
        # We should summarize messages 1-8.
        # We keep 9-20 verbatim.
        # If we have < RECENT_MESSAGES_WINDOW + SUMMARY_TRIGGER_MESSAGES, maybe wait?
        
        if len(unsummarized_messages) < SUMMARY_TRIGGER_MESSAGES:
            return
            
        # Logic: Summarize ALL unsummarized messages.
        # BUT we must consider the "Overlap".
        # If we summarize everything, then next time we load context, we load Summary + Last N.
        # If we just summarized the Last N, then we are double counting if we load them again?
        # NO. We load Summary + (All messages > summarized_until). 
        # Wait, if we summarize everything, then `summarized_until` moves to the end.
        # Then `get_context` loads messages > `summarized_until` -> which is 0 messages.
        # This means context is ONLY summary. That's bad. We want Summary + Recent verbatim.
        
        # So: usage of `summarized_until` vs `RECENT_MESSAGES_WINDOW`.
        # `get_context` loads LAST N messages (regardless of summarization status).
        # Summarization should summarize messages that are OLDER than N.
        
        # Re-calc unsummarized count considering window
        total_count = self.db.query(Message).filter(Message.conversation_id == self.conversation_id).count()
        
        # Messages eligible for summarization are those older than Window
        # i.e. indices [0 ... total - window]
        
        if total_count <= RECENT_MESSAGES_WINDOW:
            return # Nothing to summarize
            
        # We want to summarize from `summarized_until` up to `total - window`.
        # Is that range big enough?
        
        # Actually simpler:
        # Just grab the texts of unsummarized messages.
        # Append to current summary.
        # Update `summarized_until`.
        # BUT we only want to commit this to DB if we are pushing them out of the window.
        
        pass # To be implemented fully if logic is complex, but let's do a simple incremental approach:
        
        # 1. We summarize messages that are NOT in the recent window.
        eligible_to_summarize = total_count - RECENT_MESSAGES_WINDOW
        if eligible_to_summarize <= 0:
            return

        # Fetch messages to summarize (from start or after last summary, up to limit)
        # We need to find the boundary.
        
        # Easier: Fetch ALL messages, slice in python? (Maybe inefficient for huge chats, but ok for now)
        # Or smart query.
        
        # Find the message at offset `eligible_to_summarize - 1`.
        cutoff_msg = self.db.query(Message).filter(
            Message.conversation_id == self.conversation_id
        ).order_by(asc(Message.created_at)).offset(eligible_to_summarize - 1).limit(1).first()
        
        if not cutoff_msg:
            return

        # Get messages between `summarized_until` and `cutoff_msg` (inclusive)
        q = self.db.query(Message).filter(
            Message.conversation_id == self.conversation_id,
            Message.created_at <= cutoff_msg.created_at
        )
        
        if memory.summarized_until_message_id:
             last_msg = self.db.query(Message).filter(Message.id == memory.summarized_until_message_id).first()
             if last_msg:
                q = q.filter(Message.created_at > last_msg.created_at)
        
        msgs_to_summarize = q.order_by(asc(Message.created_at)).all()
        
        if len(msgs_to_summarize) < SUMMARY_TRIGGER_MESSAGES:
            return
            
        logger.info(f"Summarizing {len(msgs_to_summarize)} messages for conversation {self.conversation_id}")
        
        # Generate Summary
        text_lines = [f"{m.role}: {m.content}" for m in msgs_to_summarize]
        conversation_text = "\n".join(text_lines)
        
        current_summary = memory.summary_text or "No previous summary."
        
        summary_prompt = f"""
        Progressively summarize the conversation.
        
        Current Summary:
        {current_summary}
        
        New Lines to Add:
        {conversation_text}
        
        Update the summary to include the new information. Keep it concise, factual, and minimal.
        Focus on: decisions, user preferences, key facts, pending tasks.
        """
        
        response = await self.summarizer_llm.ainvoke([HumanMessage(content=summary_prompt)])
        new_summary = response.content
        
        # Update DB
        memory.summary_text = new_summary
        memory.summarized_until_message_id = msgs_to_summarize[-1].id
        memory.summarized_until_created_at = msgs_to_summarize[-1].created_at
        memory.summary_version += 1
        
        self.db.commit()
        logger.info("Summary updated.")
