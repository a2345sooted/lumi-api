from sqlalchemy import func
from sqlalchemy.orm import Session
from src.common.models.notes import UserNote, NoteOptimizationRun
from typing import List, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

class UserNoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, content: str, note_type: str = "Dynamic", embedding: Optional[List[float]] = None, user_id: Optional[str] = None) -> UserNote:
        db_note = UserNote(content=content, note_type=note_type, embedding=embedding, user_id=user_id)
        self.db.add(db_note)
        self.db.commit()
        self.db.refresh(db_note)
        return db_note

    def get_by_id(self, note_id: uuid.UUID) -> Optional[UserNote]:
        return self.db.query(UserNote).filter(UserNote.id == note_id).first()

    def list_all(self, user_id: Optional[str] = None) -> List[UserNote]:
        query = self.db.query(UserNote)
        if user_id:
            query = query.filter(UserNote.user_id == user_id)
        return query.order_by(UserNote.created_at.desc()).all()

    def delete(self, note_id: uuid.UUID) -> bool:
        db_note = self.get_by_id(note_id)
        if db_note:
            self.db.delete(db_note)
            self.db.commit()
            return True
        return False

    def replace_for_user(self, user_id: str, notes: List[dict]) -> None:
        """
        Replaces all notes for a user with a new set of notes.
        Each note in the list should be a dict with 'content', 'note_type', and optionally 'embedding'.
        """
        self.db.query(UserNote).filter(UserNote.user_id == user_id).delete()
        for note_data in notes:
            db_note = UserNote(
                user_id=user_id,
                content=note_data["content"],
                note_type=note_data.get("note_type", "Dynamic"),
                embedding=note_data.get("embedding")
            )
            self.db.add(db_note)
        self.db.commit()

    def start_optimization_run(self, user_id: str, thread_id: Optional[uuid.UUID] = None) -> bool:
        """
        Attempts to start an optimization run for a user.
        Returns True if the run was started, False if one is already in progress.
        A run is considered in progress if it exists and status is 'PROCESSING'.
        """
        try:
            # Check if a run already exists
            existing_run = self.db.query(NoteOptimizationRun).filter(NoteOptimizationRun.user_id == user_id).first()
            if existing_run and existing_run.status == "PROCESSING":
                return False
            
            if existing_run:
                existing_run.status = "PROCESSING"
                existing_run.thread_id = thread_id
                existing_run.started_at = func.now()
            else:
                # Create a new run
                new_run = NoteOptimizationRun(user_id=user_id, thread_id=thread_id, status="PROCESSING")
                self.db.add(new_run)
            
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error starting optimization run for user {user_id}: {e}")
            return False

    def end_optimization_run(self, user_id: str, status: str = "COMPLETED") -> None:
        """
        Ends an optimization run for a user by updating the status.
        """
        try:
            run = self.db.query(NoteOptimizationRun).filter(NoteOptimizationRun.user_id == user_id).first()
            if run:
                run.status = status
                self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error ending optimization run for user {user_id}: {e}")
