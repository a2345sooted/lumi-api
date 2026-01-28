from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from src.agents.chat.state import AgentState
from src.agents.chat.nodes.chat import chat_node
from src.agents.chat.nodes.load_notes import load_notes_node
from src.agents.chat.nodes.load_profile import load_profile_node
from src.agents.chat.tools.note_tools import save_user_note
from src.agents.chat.tools.profile_tools import update_user_profile

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def compile_chat_agent(checkpointer=None):
    workflow = StateGraph(AgentState)
    
    workflow.add_node("load_notes", load_notes_node)
    workflow.add_node("load_profile", load_profile_node)
    workflow.add_node("chat", chat_node)
    workflow.add_node("tools", ToolNode([save_user_note, update_user_profile]))
    
    workflow.add_edge(START, "load_notes")
    workflow.add_edge(START, "load_profile")
    workflow.add_edge("load_notes", "chat")
    workflow.add_edge("load_profile", "chat")
    
    workflow.add_conditional_edges(
        "chat",
        should_continue,
    )
    workflow.add_edge("tools", "chat")
    
    return workflow.compile(checkpointer=checkpointer)
