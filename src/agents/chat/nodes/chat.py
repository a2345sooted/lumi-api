from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from src.agents.chat.state import AgentState
from src.ai_constants import OPENAI_MODEL_5_2
from src.agents.chat.tools.note_tools import save_user_note
from src.agents.chat.tools.profile_tools import update_user_profile
from src.database import SessionLocal
from src.repos.chat import ConversationRepository
import uuid

async def chat_node(state: AgentState, config=None):
    llm = ChatOpenAI(model=OPENAI_MODEL_5_2, streaming=True)
    llm_with_tools = llm.bind_tools([save_user_note, update_user_profile])
    
    notes_context = ""
    if state.get("user_notes"):
        notes_context = "\n\nHere are some notes about the user:\n- " + "\n- ".join(state["user_notes"])
    
    profile_context = ""
    if state.get("user_profile"):
        profile_context = f"\n\nHere is the user's profile information:\n{state['user_profile']}"
    
    system_message = SystemMessage(content=f"You are a helpful assistant. Always respond with valid markdown.{notes_context}{profile_context}")
    messages = [system_message] + state["messages"]
    
    try:
        response = await llm_with_tools.ainvoke(messages, config=config)
        return {"messages": [response]}
    except Exception as e:
        chat_run_id = config.get("configurable", {}).get("chat_run_id") if config else None
        if chat_run_id:
            db = SessionLocal()
            try:
                chat_repo = ConversationRepository(db)
                chat_repo.end_chat_run(uuid.UUID(chat_run_id), status="FAILED")
            finally:
                db.close()
        raise e
