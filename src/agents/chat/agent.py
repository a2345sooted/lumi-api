from langgraph.graph import StateGraph, START, END
from src.agents.chat.state import AgentState
from src.agents.chat.nodes.chat import chat_node

def compile_chat_agent(checkpointer=None):
    workflow = StateGraph(AgentState)
    
    workflow.add_node("chat", chat_node)
    
    workflow.add_edge(START, "chat")
    workflow.add_edge("chat", END)
    
    return workflow.compile(checkpointer=checkpointer)
