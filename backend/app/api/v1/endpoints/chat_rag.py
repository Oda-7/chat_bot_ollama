# # ...existing code from chat_new.py...
# """
# Endpoints pour le chat avec Ollama
# """
# from fastapi import APIRouter, HTTPException, status, Depends
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from typing import List, Optional, Dict, Any
# from uuid import UUID
# import uuid

# from app.domain.entities.user import User
# from app.infrastructure.database import get_db
# from app.infrastructure.repositories import ChatRepository
# from app.core.security import get_current_user
# from app.core.logging import logger

# router = APIRouter()


# class ChatSessionCreate(BaseModel):
#     """Modèle pour créer une session de chat"""
#     title: Optional[str] = "Nouvelle conversation"



# @router.post("/session")
# async def create_session(
#     session_data: ChatSessionCreate,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """
#     Créer une nouvelle session de chat
#     """
#     try:
#         chat_repo = ChatRepository(db)
        
#         session = chat_repo.create_session(
#             user_id=current_user.id,
#             title=session_data.title
#         )
        
#         logger.info(f"Nouvelle session créée: {session.id} pour {current_user.username}")
        
#         return {
#             "session_id": session.id,
#             "title": session.title,
#             "created_at": session.created_at.isoformat(),
#             "message": "Session créée avec succès RAG"
#         }
        
#     except Exception as e:
#         logger.error(f"Erreur lors de la création de session: {e}")
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail="Erreur lors de la création de la session"
#         )






