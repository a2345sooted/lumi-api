from src.agents.chat.state import AgentState
from src.database import SessionLocal
from src.repos.profile import UserProfileRepository
import logging

logger = logging.getLogger(__name__)

async def load_profile_node(state: AgentState):
    db = SessionLocal()
    try:
        repo = UserProfileRepository(db)
        user_id = state.get("user_id")
        profile = repo.get_profile(user_id=user_id)
        
        profile_info = {}
        if profile and profile.profile_info:
            profile_info = profile.profile_info
            
        return {"user_profile": profile_info}
    except Exception as e:
        logger.error(f"Error loading user profile: {e}")
        return {"user_profile": {}}
    finally:
        db.close()
