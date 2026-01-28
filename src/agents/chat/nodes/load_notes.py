from src.agents.chat.state import AgentState
from src.database import SessionLocal
from src.repos.notes import UserNoteRepository

async def load_notes_node(state: AgentState):
    db = SessionLocal()
    try:
        repo = UserNoteRepository(db)
        user_id = state.get("user_id")
        notes = repo.list_all(user_id=user_id)
        # Extract content from notes
        note_contents = [note.content for note in notes]
        return {"user_notes": note_contents}
    finally:
        db.close()
