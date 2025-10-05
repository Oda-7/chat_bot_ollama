from sqlalchemy import Column, String, DateTime,  Boolean, UUID, ForeignKey
from sqlalchemy.sql import func
import uuid
from sqlalchemy.orm import relationship
from app.infrastructure.database import Base


class ChatSession(Base):
    """Modèle session de chat"""
    __tablename__ = "t7_chat_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("t7_users.id"), nullable=False)
    title = Column(String(200), nullable=False, default="Nouvelle conversation")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(id='{self.id}', title='{self.title}')>"