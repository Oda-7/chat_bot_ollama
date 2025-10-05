from typing import Optional, List, Any
from uuid import UUID

class IChatRepository:
    """Interface pour le repository de chat"""

    def create_session(self, user_id: UUID, title: str) -> Any:
        raise NotImplementedError

    def get_session_by_id(self, session_id: UUID) -> Optional[Any]:
        raise NotImplementedError

    def get_sessions_by_user(self, user_id: UUID) -> List[Any]:
        raise NotImplementedError

    def add_message(self, session_id: UUID, message_type: str, content: str, **kwargs) -> Any:
        raise NotImplementedError

    def get_messages_by_session(self, session_id: UUID) -> List[Any]:
        raise NotImplementedError

    def delete_session(self, session_id: UUID) -> bool:
        raise NotImplementedError