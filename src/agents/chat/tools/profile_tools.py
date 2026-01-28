from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from src.database import SessionLocal
from src.repos.notes import UserNoteRepository
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
        repo = UserNoteRepository(db)
        
        # In the new system, profile info is stored in a note of type 'Profile'.
        # We'll fetch existing profile notes and update/replace them.
        existing_notes = repo.list_all(user_id=user_id)
        profile_notes = [n for n in existing_notes if n.note_type == "Profile"]
        
        # For now, let's keep it simple: we store a summary of profile info in one Profile note.
        # We can try to parse existing profile info if it was JSON-like, but since it's now just a note,
        # we'll just append/format the new info.
        
        new_data = []
        if first_name: new_data.append(f"First Name: {first_name}")
        if last_name: new_data.append(f"Last Name: {last_name}")
        if middle_name: new_data.append(f"Middle Name: {middle_name}")
        if city: new_data.append(f"City: {city}")
        if state: new_data.append(f"State: {state}")
        if email: new_data.append(f"Email: {email}")
        
        if not new_data:
            return "No profile information provided to update."
            
        content = "User Profile Information:\n" + "\n".join(new_data)
        
        # Delete old profile notes to replace with new consolidated one
        for old_note in profile_notes:
            repo.delete(old_note.id)
            
        repo.create(content=content, note_type="Profile", user_id=user_id)
        
        return "User profile updated successfully in notes."
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return f"Failed to update user profile: {str(e)}"
    finally:
        db.close()
