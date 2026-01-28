from src.agents.chat.state import AgentState
from src.database import SessionLocal
from src.repos.notes import UserNoteRepository

async def load_notes_node(state: AgentState):
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
    finally:
        db.close()
