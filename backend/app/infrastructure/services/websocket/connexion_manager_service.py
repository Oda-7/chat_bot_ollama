from typing import Dict, List, Optional, Set
from starlette.websockets import WebSocket
from app.core.logging import logger
from datetime import datetime
import json


class ConnectionManagerService:
    """Gestionnaire des connexions WebSocket"""
    
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}
        self.user_rooms: Dict[str, Set[str]] = {}
        self.websocket_users: Dict[WebSocket, str] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        """Connecter un utilisateur à une room (avec acceptation WebSocket)"""
        await websocket.accept()
        await self.add_to_room(websocket, room_id, user_id)
    
    async def add_to_room(self, websocket: WebSocket, room_id: str, user_id: str):
        """Ajouter un utilisateur à une room (connexion déjà acceptée)"""
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        
        self.rooms[room_id][user_id] = websocket
        
        if user_id not in self.user_rooms:
            self.user_rooms[user_id] = set()
        self.user_rooms[user_id].add(room_id)
        self.websocket_users[websocket] = user_id
        
        logger.info(f"Utilisateur {user_id} ajouté à la room {room_id}")
        
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "room_id": room_id
        }, exclude_user=user_id)
    
    async def disconnect(self, websocket: WebSocket):
        """Déconnecter un utilisateur"""
        if websocket not in self.websocket_users:
            return
        
        user_id = self.websocket_users[websocket]
        rooms_to_clean = []
        
        for room_id in self.user_rooms.get(user_id, []):
            if room_id in self.rooms and user_id in self.rooms[room_id]:
                del self.rooms[room_id][user_id]
                
                await self.broadcast_to_room(room_id, {
                    "type": "user_left",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "room_id": room_id
                }, exclude_user=user_id)
                
                if not self.rooms[room_id]:
                    rooms_to_clean.append(room_id)
        
        for room_id in rooms_to_clean:
            del self.rooms[room_id]
        
        if user_id in self.user_rooms:
            del self.user_rooms[user_id]
        if websocket in self.websocket_users:
            del self.websocket_users[websocket]
        
        logger.info(f"Utilisateur {user_id} déconnecté")
    
    async def send_personal_message(self, message: Dict, user_id: str):
        """Envoyer un message à un utilisateur spécifique"""
        for room_id, users in self.rooms.items():
            if user_id in users:
                try:
                    await users[user_id].send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Erreur envoi message à {user_id}: {e}")
    
    async def broadcast_to_room(self, room_id: str, message: Dict, exclude_user: Optional[str] = None):
        """Diffuser un message à tous les utilisateurs d'une room"""
        if room_id not in self.rooms:
            return
        
        message_str = json.dumps(message)
        disconnected_users = []
        
        for user_id, websocket in self.rooms[room_id].items():
            if exclude_user and user_id == exclude_user:
                continue
            
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Erreur diffusion à {user_id} dans room {room_id}: {e}")
                disconnected_users.append((websocket, user_id))
        
        for websocket, user_id in disconnected_users:
            await self.disconnect(websocket)
    
    def get_room_users(self, room_id: str) -> List[str]:
        """Récupérer la liste des utilisateurs d'une room"""
        if room_id not in self.rooms:
            return []
        return list(self.rooms[room_id].keys())
    
    def get_user_count(self, room_id: str) -> int:
        """Compter les utilisateurs dans une room"""
        return len(self.get_room_users(room_id))


