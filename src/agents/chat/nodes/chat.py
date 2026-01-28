from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from src.agents.chat.state import AgentState
from src.ai_constants import OPENAI_MODEL_5_2
from src.agents.chat.tools.note_tools import save_user_note
from src.agents.chat.tools.profile_tools import update_user_profile

async def chat_node(state: AgentState):
    llm = ChatOpenAI(model=OPENAI_MODEL_5_2, streaming=True)
    llm_with_tools = llm.bind_tools([save_user_note, update_user_profile])
    
    notes_context = ""
    if state.get("user_notes"):
        notes_context = "\n\nHere are some notes about the user:\n- " + "\n- ".join(state["user_notes"])
    
    profile_context = ""
    if state.get("user_profile"):
        profile_context = "\n\nHere is the user's profile information:\n" + "\n".join([f"- {k}: {v}" for k, v in state["user_profile"].items()])
    
    system_message = SystemMessage(content=f"You are a helpful assistant. Always respond with valid markdown.{notes_context}{profile_context}")
    messages = [system_message] + state["messages"]
    
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}
