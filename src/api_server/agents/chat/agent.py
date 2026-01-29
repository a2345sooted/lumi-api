from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from src.api_server.agents.chat.state import AgentState
from src.api_server.agents.chat.nodes.chat import chat_node
from src.api_server.agents.chat.nodes.load_notes import load_notes_node
from src.api_server.agents.chat.nodes.load_current_time import load_current_time_node
from src.api_server.agents.chat.tools.note_tools import save_user_note
from src.api_server.agents.chat.tools.profile_tools import update_user_profile
from src.api_server.agents.chat.router import should_continue

def compile_chat_agent(checkpointer=None):
    workflow = StateGraph(AgentState)
    
    workflow.add_node("load_current_time", load_current_time_node)
    workflow.add_node("load_notes", load_notes_node)
    workflow.add_node("chat", chat_node)
    workflow.add_node("tools", ToolNode([save_user_note, update_user_profile]))
    
    workflow.add_edge(START, "load_current_time")
    workflow.add_edge("load_current_time", "load_notes")
    workflow.add_edge("load_notes", "chat")
    
    workflow.add_conditional_edges(
        "chat",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    workflow.add_edge("tools", "chat")
    
    return workflow.compile(checkpointer=checkpointer)
