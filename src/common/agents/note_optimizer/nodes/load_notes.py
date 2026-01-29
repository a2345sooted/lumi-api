from src.common.agents.note_optimizer.state import NoteOptimizerState
from src.common.database import SessionLocal
from src.common.repos.notes import UserNoteRepository

async def load_notes_node(state: NoteOptimizerState):
    db = SessionLocal()
    try:
        repo = UserNoteRepository(db)
        user_id = state.get("user_id")
        notes = repo.list_all(user_id=user_id)
        
        original_notes = [
            {
                "content": note.content, 
                "note_type": note.note_type,
                "created_at": note.created_at.isoformat() if note.created_at else None
            }
            for note in notes
        ]
        
        return {
            "original_notes": original_notes
        }
    except Exception as e:
        repo = UserNoteRepository(db)
        repo.end_optimization_run(state.get("user_id"), status="FAILED")
        raise e
    finally:
        db.close()
