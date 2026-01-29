from typing import Any

# Global agent instances
_chat_agent = None
_note_optimizer_agent = None

def register_chat_agent(agent: Any):
    global _chat_agent
    _chat_agent = agent

def get_chat_agent():
    if _chat_agent is None:
        raise RuntimeError("Chat Agent not compiled. Ensure compilation happens during startup.")
    return _chat_agent

def register_note_optimizer_agent(agent: Any):
    global _note_optimizer_agent
    _note_optimizer_agent = agent

def get_note_optimizer_agent():
    if _note_optimizer_agent is None:
        raise RuntimeError("Note Optimizer Agent not compiled. Ensure compilation happens during startup.")
    return _note_optimizer_agent
