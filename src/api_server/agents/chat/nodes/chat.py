from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from src.api_server.agents.chat.state import AgentState
from src.common.ai_constants import OPENAI_MODEL_5_2
from src.api_server.agents.chat.tools.note_tools import save_user_note
from src.api_server.agents.chat.tools.profile_tools import update_user_profile
from src.api_server.agents.chat.tools.personality_tools import get_assistant_info
from src.api_server.agents.chat.tools.health_tools import get_hydration_rubric
from src.common.database import SessionLocal
from src.common.repos.chat import UserMessageRepository
import uuid

async def chat_node(state: AgentState, config=None):
    llm = ChatOpenAI(model=OPENAI_MODEL_5_2, streaming=True)
    llm_with_tools = llm.bind_tools([save_user_note, update_user_profile, get_assistant_info, get_hydration_rubric])
    
    notes_context = ""
    if state.get("user_notes"):
        notes_context = "\n\nHere are some notes about the user:\n- " + "\n- ".join(state["user_notes"])
    
    profile_context = ""
    if state.get("user_profile"):
        profile_context = f"\n\nHere is the user's profile information:\n{state['user_profile']}"
    
    time_context = ""
    if state.get("current_time"):
        time_context = f"\n\nCurrent time: {state['current_time']}"
    
    system_message = SystemMessage(content=(
        "You are Lumi, a Mind, Body, and Spirit Assistant. Always respond with valid markdown. "
        "Your mission is to help the user harmonize their diet, hydration, exercise, mindfulness, and spirituality. "
        "The user's information (notes and profile) might be provided in JSON format; "
        "if so, treat the JSON keys and values as facts about the user. "
        "If the user asks about you, your personality, your mission, your hobbies, or your preferences, "
        "use the 'get_assistant_info' tool to provide accurate information about yourself. "
        "If the user asks about their hydration needs or how much water they should drink, "
        "use the 'get_hydration_rubric' tool to retrieve the evidence-based guidelines and calculate a personalized goal. "
        "Always provide volume measurements in ounces (oz). "
        "Crucially, when the user provides personal information (such as weight, sex, age, activity level, or preferences), "
        "you MUST save this information using the 'save_user_note' tool (with note_type='Profile' for biological/demographic data) "
        "to ensure it is remembered for future interactions. "
        "Maintain a friendly, encouraging, and occasionally witty tone while staying focused on holistic wellness."
        f"{notes_context}{profile_context}{time_context}"
    ))
    messages = [system_message] + state["messages"]
    
    try:
        response = await llm_with_tools.ainvoke(messages, config=config)
        return {"messages": [response]}
    except Exception as e:
        chat_run_id = config.get("configurable", {}).get("chat_run_id") if config else None
        if chat_run_id:
            db = SessionLocal()
            try:
                message_repo = UserMessageRepository(db)
                message_repo.end_chat_run(uuid.UUID(chat_run_id), status="FAILED")
            finally:
                db.close()
        raise e
