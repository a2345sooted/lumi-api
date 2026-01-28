from src.agents.chat.state import AgentState
from langgraph.graph import END

def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END
