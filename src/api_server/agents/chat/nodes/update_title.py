from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from src.api_server.agents.chat.state import AgentState
from src.common.ai_constants import OPENAI_MODEL_4O_MINI
from src.common.database import SessionLocal
from src.common.repos.chat import ConversationRepository
from src.common.services.websocket_manager import manager
import uuid
import logging

logger = logging.getLogger(__name__)

async def update_title_node(state: AgentState, config=None):
    messages = state["messages"]
    
    thread_id_str = config.get("configurable", {}).get("thread_id") if config else None
    if not thread_id_str:
        return {}

    db = SessionLocal()
    try:
        repo = ConversationRepository(db)
        
        llm = ChatOpenAI(model=OPENAI_MODEL_4O_MINI, temperature=0)
        
        # Prepare conversation history for naming
        history = ""
        for m in messages:
            role = "User" if m.type == "human" else "Assistant"
            history += f"{role}: {m.content}\n"
        
        prompt = f"Based on the following conversation, provide a very short, concise title (max 6 words).\n\n{history}\n\nTitle:"
        
        response = await llm.ainvoke([HumanMessage(content=prompt)])
        new_title = response.content.strip().strip('"')
        
        repo.update_title(uuid.UUID(thread_id_str), new_title)
        logger.info(f"Updated conversation {thread_id_str} title to: {new_title}")
        
        # Send WebSocket event to user
        user_id = state.get("user_id")
        if user_id:
            await manager.send_to_user(user_id, {
                "type": "conversation_title_updated",
                "conversation_id": thread_id_str,
                "title": new_title
            })
            
    except Exception as e:
        logger.error(f"Error updating conversation title: {e}")
        # We don't want to fail the whole chat if title update fails
    finally:
        db.close()
        
    return {}
