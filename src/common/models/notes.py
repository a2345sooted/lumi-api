from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import VECTOR
from src.common.database import Base
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

class NoteOptimizationRun(Base):
    __tablename__ = "note_optimization_runs"

    user_id = Column(String, primary_key=True)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=True)
    status = Column(String, nullable=False, server_default="PROCESSING")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
