from sqlalchemy.orm import Session
from src.models.notes import UserNote
from typing import List, Optional
import uuid

class UserNoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, content: str, embedding: Optional[List[float]] = None, user_id: Optional[str] = None) -> UserNote:
        db_note = UserNote(content=content, embedding=embedding, user_id=user_id)
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
