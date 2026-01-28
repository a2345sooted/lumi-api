from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from src.database import SessionLocal
from src.repos.profile import UserProfileRepository
from typing import Optional
import logging

logger = logging.getLogger(__name__)

@tool
def update_user_profile(
    config: RunnableConfig,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    middle_name: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    email: Optional[str] = None
) -> str:
    """
    Updates the user's profile information. Use this when the user shares personal details 
    like their name, location, or contact info.
    """
    user_id = config.get("configurable", {}).get("user_id")
    db = SessionLocal()
    try:
        repo = UserProfileRepository(db)
        
        profile_data = {}
        if first_name is not None: profile_data["first_name"] = first_name
        if last_name is not None: profile_data["last_name"] = last_name
        if middle_name is not None: profile_data["middle_name"] = middle_name
        if city is not None: profile_data["city"] = city
        if state is not None: profile_data["state"] = state
        if email is not None: profile_data["email"] = email
        
        if not profile_data:
            return "No profile information provided to update."
            
        repo.update_profile(profile_data, user_id=user_id)
        return "User profile updated successfully."
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return f"Failed to update user profile: {str(e)}"
    finally:
        db.close()
