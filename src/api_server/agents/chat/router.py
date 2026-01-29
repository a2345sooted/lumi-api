from src.api_server.agents.chat.state import AgentState
from langgraph.graph import END

def should_update_title(state: AgentState) -> bool:
    messages = state["messages"]
    user_msg_count = sum(1 for m in messages if m.type == "human")
    assistant_msg_count = sum(1 for m in messages if m.type == "ai")
    
    return user_msg_count in [3, 10, 20] and assistant_msg_count >= 2

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    
    if should_update_title(state):
        return "update_title"
        
    return END
