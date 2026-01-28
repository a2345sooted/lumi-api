from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from src.database import SessionLocal
from src.repos.notes import UserNoteRepository
from src.services.embeddings import embeddings_service
import logging

logger = logging.getLogger(__name__)

@tool
def save_user_note(content: str, config: RunnableConfig, note_type: str = "Dynamic") -> str:
    """
    Saves a note about the user. Use this when the user shares something 
    important about themselves that should be remembered.
    
    Args:
        content: The content of the note to save.
        note_type: The type of note. Use 'Profile' for personal info (name, email, etc.) and 'Dynamic' for other facts. Defaults to 'Dynamic'.
    """
    user_id = config.get("configurable", {}).get("user_id")
    db = SessionLocal()
    try:
        repo = UserNoteRepository(db)
        
        # Generate embedding
        embedding = embeddings_service.embed_query(content)
        
        note = repo.create(content=content, note_type=note_type, embedding=embedding, user_id=user_id)
        return f"Note saved successfully with ID: {note.id}"
    except Exception as e:
        logger.error(f"Error saving user note: {e}")
        return f"Failed to save note: {str(e)}"
    finally:
        db.close()
