from typing import Optional, List
from sqlalchemy.orm import Session
from app.domain.interfaces.repositories.chat.i_chat_repository import IChatRepository
from app.domain.entities.chat_message import ChatMessage
from app.domain.entities.chat_session import ChatSession
from uuid import UUID

class ChatRepository(IChatRepository):
    """Repository pour la gestion des chats"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_session(self, user_id: UUID, title: str = "Nouvelle conversation") -> ChatSession:
        """Créer une nouvelle session de chat"""
        session = ChatSession(
            user_id=user_id,
            title=title
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_sessions_by_user(self, user_id: UUID, active_only: bool = True) -> List[ChatSession]:
        """Récupérer les sessions d'un utilisateur"""
        query = self.db.query(ChatSession).filter(ChatSession.user_id == user_id)
        if active_only:
            query = query.filter(ChatSession.is_active)
        return query.order_by(ChatSession.created_at.desc()).all()
    
    def get_session_by_id(self, session_id: UUID) -> Optional[ChatSession]:
        """Récupérer une session par ID"""
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    def add_message(
        self,
        session_id: UUID,
        message_type: str,  
        content: str,
        llm_used: Optional[str] = None,
        tokens_used: Optional[int] = None,
        response_time: Optional[int] = None
    ) -> ChatMessage:
        """Ajouter un message à une session"""
        message = ChatMessage(
            session_id=session_id,
            message_type=message_type,
            content=content,
            llm_used=llm_used,
            tokens_used=tokens_used,
            response_time=response_time
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_session_messages(self, session_id: UUID) -> List[ChatMessage]:
        """Récupérer tous les messages d'une session"""
        return self.db.query(ChatMessage)\
            .filter(ChatMessage.session_id == session_id)\
            .order_by(ChatMessage.created_at.asc())\
            .all()
    
    def update_session_title(self, session_id: UUID, title: str) -> Optional[ChatSession]:
        """Mettre à jour le titre d'une session"""
        session = self.get_session_by_id(session_id)
        if not session:
            return None
        
        session.title = title
        self.db.commit()
        self.db.refresh(session)
        return session
    
    def get_session_by_id(self, session_id: UUID, user_id: UUID) -> Optional[ChatSession]:
        """Récupérer une session par ID et utilisateur (sécurité)"""
        return self.db.query(ChatSession)\
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)\
            .first()
    
    def create_message(
        self,
        session_id: UUID,
        message_type: str, 
        content: str,
        llm_used: Optional[str] = None,
        tokens_used: Optional[int] = None,
        response_time: Optional[int] = None
    ) -> ChatMessage:
        """Créer un nouveau message (alias pour add_message)"""
        return self.add_message(
            session_id=session_id,
            message_type=message_type,
            content=content,
            llm_used=llm_used,
            tokens_used=tokens_used,
            response_time=response_time
        )
    
    def get_sessions_by_user(self, user_id: UUID, limit: int = 20) -> List[ChatSession]:
        """Récupérer les sessions d'un utilisateur avec limite"""
        return self.db.query(ChatSession)\
            .filter(ChatSession.user_id == user_id)\
            .order_by(ChatSession.updated_at.desc())\
            .limit(limit)\
            .all()
    
    def delete_session(self, session_id: UUID) -> bool:
        """Supprimer une session et tous ses messages"""
        session = self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return False
        
        self.db.delete(session)
        self.db.commit()
        return True