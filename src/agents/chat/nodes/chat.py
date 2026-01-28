from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from src.agents.chat.state import AgentState
from src.ai_constants import OPENAI_MODEL_5_2

async def chat_node(state: AgentState):
    llm = ChatOpenAI(model=OPENAI_MODEL_5_2, streaming=True)
    
    system_message = SystemMessage(content="You are a helpful assistant. Always respond with valid markdown.")
    messages = [system_message] + state["messages"]
    
    response = await llm.ainvoke(messages)
    return {"messages": [response]}
