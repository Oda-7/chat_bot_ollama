from sqlalchemy import Column, Integer, DateTime, Text,  ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database import Base
import uuid

class DocumentChunk(Base):
    """Modèle chunk de document avec embedding vectoriel"""
    __tablename__ = "t7_document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("t7_documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)  
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  
    token_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    document = relationship("Document", back_populates="chunks")

    def __repr__(self):
        return f"<DocumentChunk(doc_id='{self.document_id}', index={self.chunk_index})>"