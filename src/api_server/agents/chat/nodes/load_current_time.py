import os
from datetime import datetime, timedelta, timezone
from src.api_server.agents.chat.state import AgentState

async def load_current_time_node(state: AgentState):
    # Default is CST (UTC-6).
    timezone_offset = int(os.getenv("TIMEZONE_OFFSET", "-6"))
    timezone_name = os.getenv("TIMEZONE_NAME", "CST")
    
    tz = timezone(timedelta(hours=timezone_offset))
    now = datetime.now(timezone.utc).astimezone(tz)
    
    current_time_str = now.strftime(f"%Y-%m-%d %H:%M:%S {timezone_name}")
    
    return {
        "current_time": current_time_str
    }
