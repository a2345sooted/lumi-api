from src.agents.chat.state import AgentState
from src.database import SessionLocal
from src.repos.notes import UserNoteRepository
from src.repos.chat import ConversationRepository
import uuid

async def load_notes_node(state: AgentState, config=None):
    db = SessionLocal()
    try:
        repo = UserNoteRepository(db)
        user_id = state.get("user_id")
        notes = repo.list_all(user_id=user_id)
        
        dynamic_notes = [note.content for note in notes if note.note_type == "Dynamic"]
        profile_notes = [note.content for note in notes if note.note_type == "Profile"]
        
        # We expect only one profile note for now, but joining them just in case
        profile_content = "\n".join(profile_notes)
        
        return {
            "user_notes": dynamic_notes,
            "user_profile": profile_content
        }
    except Exception as e:
        chat_run_id = config.get("configurable", {}).get("chat_run_id")
        if chat_run_id:
            chat_repo = ConversationRepository(db)
            chat_repo.end_chat_run(uuid.UUID(chat_run_id), status="FAILED")
        raise e
    finally:
        db.close()
