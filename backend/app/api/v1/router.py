"""
Router principal API v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, health, websocket, rag, chat_classic, chat_rag

api_router = APIRouter()

# Routes publiques
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Routes protégées
api_router.include_router(chat_classic.router, prefix="/chat", tags=["Chat Classic"])
# api_router.include_router(chat_rag.router, prefix="/chat-rag", tags=["Chat RAG"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])

