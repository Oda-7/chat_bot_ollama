from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database import Base
import uuid

class Document(Base):
    """Modèle document pour RAG"""
    __tablename__ = "t7_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("t7_users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=False) 
    content_preview = Column(Text, nullable=True)  
    content = Column(Text, nullable=False)  
    chunk_count = Column(Integer, default=0)
    status = Column(String(20), default='processing') 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document(filename='{self.filename}', status='{self.status}')>"