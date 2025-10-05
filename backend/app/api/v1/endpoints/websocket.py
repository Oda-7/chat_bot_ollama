"""
Endpoints WebSocket pour chat temps réel
"""
from fastapi import APIRouter, WebSocket, Query
from sqlalchemy.orm import Session
from app.core.logging import logger
from app.infrastructure.database import SessionLocal
from app.infrastructure.services.websocket.websocket_chat_service import websocket_chat_service

router = APIRouter()


@router.websocket("/chat/{session_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    session_id: str,
    token: str = Query(...),
):
    """
    Endpoint WebSocket pour chat temps réel
    
    Paramètres:
    - session_id: ID de la session de chat
    - token: Token JWT pour l'authentification (query param)
    
    Messages supportés:
    - chat_message: Envoyer un message de chat
    - typing: Indiquer que l'utilisateur tape
    - stop_typing: Arrêter l'indicateur de frappe
    - ping: Maintenir la connexion vivante
    """
    logger.info(f"[DEBUG] Appel route WebSocket: session_id={session_id}, token={token[:20]}")
    logger.info(f"🔌 Nouvelle connexion WebSocket pour session {session_id}")
    logger.info(f"🔑 Token reçu: {token[:20]}...")
    
    db = SessionLocal()
    try:
        await websocket_chat_service.handle_websocket_connection(
            websocket, session_id, token, db
        )
    finally:
        db.close()


@router.get("/ws/rooms/{session_id}/users")
async def get_room_users(session_id: str):
    """Récupérer la liste des utilisateurs connectés dans une room"""
    users = websocket_chat_service.connection_manager.get_room_users(session_id)
    return {
        "session_id": session_id,
        "users": users,
        "user_count": len(users)
    }


@router.get("/ws/stats")
async def get_websocket_stats():
    """Statistiques des connexions WebSocket"""
    manager = websocket_chat_service.connection_manager
    
    return {
        "total_rooms": len(manager.rooms),
        "total_connections": sum(len(users) for users in manager.rooms.values()),
        "rooms": {
            room_id: {
                "user_count": len(users),
                "users": list(users.keys())
            }
            for room_id, users in manager.rooms.items()
        }
    }


@router.websocket("/test-simple")
async def test_simple_websocket(websocket: WebSocket):
    print("🔥 ROUTE SIMPLE ATTEINTE")
    await websocket.accept()
    await websocket.send_text('{"status": "simple works"}')
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Simple: {data}")
    except:
        pass


@router.websocket("/test-with-params/{session_id}")
async def test_with_params(websocket: WebSocket, session_id: str, token: str = Query(...)):
    print(f"🔥 ROUTE AVEC PARAMS ATTEINTE - session: {session_id}, token: {token[:20]}")
    
    db = SessionLocal()
    try:
        await websocket.accept()
        await websocket.send_text(f'{{"status": "params work", "session_id": "{session_id}"}}')
        
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Params echo: {data}")
    except Exception as e:
        print(f"🔥 ERREUR PARAMS: {e}")
    finally:
        db.close()