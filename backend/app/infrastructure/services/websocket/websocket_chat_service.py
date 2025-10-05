

import asyncio
from datetime import datetime
import json
from typing import Any, Dict, Optional
from app.core.logging import logger
from app.core.security import verify_token
from starlette.websockets import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from fastapi import status
from app.infrastructure.repositories.chat.chat_repository import ChatRepository
from app.infrastructure.services.ollama.ollama_service import OllamaService
from app.infrastructure.services.rag.rag_service import RagService
from app.infrastructure.services.websocket.connexion_manager_service import ConnectionManagerService


class WebSocketChatService:
    """Service de chat WebSocket avec IA et RAG"""
    
    def __init__(self):
        self.connection_manager = ConnectionManagerService()
        self.ollama_service = OllamaService()
        self.active_ai_tasks: Dict[str, asyncio.Task] = {}
    
    async def authenticate_websocket(self, token: str) -> Optional[Dict[str, Any]]:
        """Authentifier une connexion WebSocket via JWT"""
        try:
            logger.info(f"Tentative d'authentification WebSocket avec token: {token[:20]}...")
            payload = verify_token(token)
            if payload is None:
                logger.error("Échec de vérification du token JWT - payload None")
                return None
            
            logger.info(f"Payload JWT décodé: {payload}")
            user_id = payload.get("user_id")
            username = payload.get("sub")
            
            if not user_id or not username:
                logger.error(f"Payload JWT incomplet - user_id: {user_id}, username: {username}")
                return None
            
            logger.info(f"Authentification WebSocket réussie pour user_id: {user_id}, username: {username}")
            return {
                "user_id": user_id,
                "username": username
            }
        except Exception as e:
            logger.error(f"Erreur authentification WebSocket: {e}")
            return None
    
    async def handle_websocket_connection(
        self, 
        websocket: WebSocket, 
        session_id: str,
        token: str,
        db: Session
    ):
        """Gérer une connexion WebSocket complète"""

        logger.info(f"WebSocket: Connexion reçue - session_id={session_id}, token={token[:50]}...")
        
        user_info = await self.authenticate_websocket(token)
        logger.info(f"WebSocket: Résultat authentification - user_info={user_info}")
        if not user_info:
            logger.error(f"WebSocket refuse: Invalid token {token[:50]}...")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
            return

        user_id = user_info["user_id"]
        username = user_info["username"]

        chat_repo = ChatRepository(db)
        session = chat_repo.get_session_by_id(session_id, user_id)
        logger.info(f"WebSocket: Résultat récupération session - session trouvée: {session is not None}")
        if not session:
            logger.error(f"WebSocket refuse: Session not found - session_id={session_id}, user_id={user_id}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Session not found or not owned by user")
            return
        
        try:
            await websocket.accept()
            logger.info(f"✅ Connexion WebSocket acceptée pour {username}")
            
            await self.connection_manager.add_to_room(websocket, session_id, user_id)
            
            await websocket.send_text(json.dumps({
                "type": "connection_established",
                "session_id": session_id,
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.utcnow().isoformat()
            }))
            
            while True:
                logger.info(f"[{username}] En attente de message WebSocket...")
                data = await websocket.receive_text()
                
                if not data.strip():
                    logger.warning(f"[{username}] Message vide reçu, ignoré")
                    continue
                logger.info(f"[{username}] Message reçu: {data[:100]}...")
                
                try:
                    message_data = json.loads(data)
                except json.JSONDecodeError as e :
                    logger.error(f"[{username}] Erreur décodage JSON: {e}")
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON format",
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                    continue
                
                
                await self.handle_message(
                    message_data, 
                    session_id, 
                    user_id, 
                    username,
                    websocket,
                    db
                )
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket déconnecté pour {username}")
            if session_id in self.active_ai_tasks:
                task = self.active_ai_tasks[session_id]
                if not task.done():
                    logger.info(f"Annulation de la tâche IA en cours pour session {session_id}")
                    task.cancel()
                del self.active_ai_tasks[session_id]
            await self.connection_manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"Erreur WebSocket pour {username}: {e}")
            if session_id in self.active_ai_tasks:
                task = self.active_ai_tasks[session_id]
                if not task.done():
                    task.cancel()
                del self.active_ai_tasks[session_id]
            await self.connection_manager.disconnect(websocket)
    
    async def handle_message(
        self,
        message_data: Dict[str, Any],
        session_id: str,
        user_id: str,
        username: str,
        websocket: WebSocket,
        db: Session
    ):
        """Traiter un message reçu via WebSocket"""
        try:
            message_type = message_data.get("type")
            
            if message_type == "chat_message":
                await self.handle_chat_message(message_data, session_id, user_id, username, websocket, db)
            
            elif message_type == "typing":
                await self.connection_manager.broadcast_to_room(session_id, {
                    "type": "user_typing",
                    "user_id": user_id,
                    "username": username,
                    "timestamp": datetime.utcnow().isoformat()
                }, exclude_user=user_id)
            
            elif message_type == "stop_typing":
                await self.connection_manager.broadcast_to_room(session_id, {
                    "type": "user_stopped_typing",
                    "user_id": user_id,
                    "username": username,
                    "timestamp": datetime.utcnow().isoformat()
                }, exclude_user=user_id)
            
            else:
                logger.warning(f"Type de message non supporté: {message_type}")
        
        except Exception as e:
            logger.error(f"Erreur traitement message WebSocket: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Erreur lors du traitement du message",
                "timestamp": datetime.utcnow().isoformat()
            }))
    
    async def handle_chat_message(
        self,
        message_data: Dict[str, Any],
        session_id: str,
        user_id: str,
        username: str,
        websocket: WebSocket,
        db: Session
    ):
        """Traiter un message de chat avec IA"""
        try:
            content = message_data.get("content", "").strip()
            if not content:
                return
            
            use_rag = message_data.get("use_rag", True)
            model = message_data.get("model", "mistral:7b")
            
            chat_repo = ChatRepository(db)
            rag_service = RagService()
            
            user_message = chat_repo.create_message(
                session_id=session_id,
                message_type="user",
                content=content
            )
            
            await self.connection_manager.broadcast_to_room(session_id, {
                "type": "user_message",
                "message_id": str(user_message.id),
                "user_id": user_id,
                "username": username,
                "content": content,
                "timestamp": user_message.created_at.isoformat()
            })
            
            await self.connection_manager.broadcast_to_room(session_id, {
                "type": "ai_thinking",
                "timestamp": datetime.utcnow().isoformat()
            })
            
            rag_context = ""
            if use_rag:
                relevant_chunks = await rag_service.retrieve_relevant_chunks(
                    content, user_id, db
                )
                if relevant_chunks:
                    rag_context = rag_service.build_rag_context(relevant_chunks)
                    
                if rag_context is None:
                    rag_context = ""
            
            async def generate_ai_response():
                try:
                    response_chunks = []
                    start_time = datetime.now()
                    async for chunk in self.ollama_service.generate_stream_response(
                        prompt=content,
                        model=model,
                        context=rag_context,
                        max_tokens=1000,
                        temperature=0.7
                    ):
                        response_chunks.append(chunk)
                        await websocket.send_text(json.dumps({
                            "type": "ai_message_stream",
                            "content": chunk,
                            "timestamp": datetime.now().isoformat()
                        }))
                    full_response = "".join(response_chunks)
                    response_time = int((datetime.now() - start_time).total_seconds() * 1000)
                    ai_message = chat_repo.create_message(
                        session_id=session_id,
                        message_type="assistant",
                        content=full_response,
                        llm_used=model,
                        tokens_used=len(full_response.split()),
                        response_time=response_time
                    )
                    
                    await self.connection_manager.broadcast_to_room(session_id, {
                        "type": "ai_message",
                        "message_id": str(ai_message.id),
                        "content": full_response,
                        "llm_used": model,
                        "response_time": response_time,
                        "tokens_used": len(full_response.split()),
                        "timestamp": ai_message.created_at.isoformat()
                    })
                except asyncio.CancelledError:
                    logger.info(f"Génération IA annulée pour session {session_id}")
                    
                except Exception as e:
                    logger.error(f"Erreur génération IA pour session {session_id}: {e}")
                    try:
                        await websocket.send_text(json.dumps({
                            "type": "ai_error",
                            "error": str(e),
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                    except Exception:
                        pass  
                finally:
                    if session_id in self.active_ai_tasks:
                        del self.active_ai_tasks[session_id]
            
            task = asyncio.create_task(generate_ai_response())
            self.active_ai_tasks[session_id] = task
        
        except Exception as e:
            logger.error(f"Erreur traitement message chat: {e}")
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Erreur lors du traitement du message",
                "timestamp": datetime.utcnow().isoformat()
            }))


websocket_chat_service = WebSocketChatService()