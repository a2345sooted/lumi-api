from src.agents.note_optimizer.state import NoteOptimizerState
from src.database import SessionLocal
from src.repos.notes import UserNoteRepository
from src.services.embeddings import embeddings_service
import logging

logger = logging.getLogger(__name__)

async def update_notes_node(state: NoteOptimizerState):
    db = SessionLocal()
    try:
        repo = UserNoteRepository(db)
        user_id = state.get("user_id")
        optimized_notes = state.get("optimized_notes", [])
        
        logger.info(f"Optimizing/Updating notes for user {user_id}. Found {len(optimized_notes)} notes.")
        
        # Prepare notes with embeddings
        notes_with_embeddings = []
        for note in optimized_notes:
            embedding = embeddings_service.embed_query(note["content"])
            notes_with_embeddings.append({
                "content": note["content"],
                "note_type": note["note_type"],
                "embedding": embedding
            })
        
        repo.replace_for_user(user_id, notes_with_embeddings)
        logger.info(f"Successfully updated notes for user {user_id}")
        
        # End the optimization run with COMPLETED status
        repo.end_optimization_run(user_id, status="COMPLETED")
        
        return {
            "optimized_notes": optimized_notes
        }
    except Exception as e:
        logger.error(f"Error in update_notes_node for user {state.get('user_id')}: {e}")
        repo = UserNoteRepository(db)
        repo.end_optimization_run(state.get("user_id"), status="FAILED")
        raise e
    finally:
        db.close()
