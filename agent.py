# agent.py (Final, Upgraded Version)

import os
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import get_all_tools

# 1. Create the LLM instance - UPGRADED TO THE PRO MODEL
from google.generativeai.types import HarmCategory, HarmBlockThreshold

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash-latest",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)

# 2. Create the Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are "VICTUS", a task-oriented AI assistant. Your purpose is to use your tools to help the user accomplish their goals efficiently.

**Reasoning Process**:
1.  **Analyze Intent**: Understand the user's goal (e.g., they want to see email, they want to open an app, they want to type text).
2.  **Gather Information**: If a tool needs more info, you MUST ask the user for the missing details.
3.  **Select & Execute**: Choose the best tool and use it immediately.

**CRITICAL RULES**:
- **UI Automation**: For tasks involving typing, screenshots, or managing windows, you must use the 'type_text', 'take_screenshot', or 'get_active_window_title' tools. Always confirm which window is active before typing.
- **Messaging Workflow**: You CANNOT send messages in apps like WhatsApp directly. Instead, use the workflow: 1. `set_clipboard_content` with the message. 2. `open_app` to launch the app. 3. Inform the user you have done so.
- **Tool Usage**: You are FORBIDDEN from refusing to use a tool you have.
- **Credentials**: You must NEVER ask for passwords. Tools handle authentication.
"""),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 3. Factory Function to Create the Agent
def create_agent_executor(rag_enabled: bool):
    """Creates a new AgentExecutor instance with the appropriate tools."""
    tools = get_all_tools(rag_enabled)
    
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # VERBOSE IS NOW FALSE to remove terminal clutter
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=False, 
        handle_parsing_errors=True
    )
    
    return agent_executor