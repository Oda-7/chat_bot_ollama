from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.infrastructure.database import Base
import uuid

class ChatMessage(Base):
    """Modèle message de chat"""
    __tablename__ = "t7_chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("t7_chat_sessions.id"), nullable=False)
    message_type = Column(String(20), nullable=False)  
    content = Column(Text, nullable=False)
    llm_used = Column(String(50), nullable=True)  
    tokens_used = Column(Integer, nullable=True)
    response_time = Column(Integer, nullable=True)  
    rag_sources = Column(Text, nullable=True) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(type='{self.message_type}', content='{self.content[:50]}...')>"