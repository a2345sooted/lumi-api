from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import VECTOR
from src.database import Base
import uuid

class UserNote(Base):
    __tablename__ = "user_notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String, nullable=True)
    content = Column(String, nullable=False)
    note_type = Column(String, nullable=False, server_default="Dynamic")
    embedding = Column(VECTOR(1536))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
