from datetime import datetime, timedelta, timezone
from src.agents.chat.state import AgentState

async def load_current_time_node(state: AgentState):
    # CST is UTC-6.
    # We'll use a fixed offset of -6 hours for CST as requested.
    cst_tz = timezone(timedelta(hours=-6))
    now = datetime.now(timezone.utc).astimezone(cst_tz)
    
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S CST")
    
    return {
        "current_time": current_time_str
    }
