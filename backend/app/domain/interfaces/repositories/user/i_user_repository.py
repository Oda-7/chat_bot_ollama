from typing import Optional, Any
from uuid import UUID

class IUserRepository:
    """Interface pour le repository utilisateur"""

    def create_user(self, username: str, email: str, password: str) -> Any:
        raise NotImplementedError
    
    def get_user_by_id(self, user_id: str) -> Optional[Any]:
        raise NotImplementedError

    def get_user_by_username(self, username: str) -> Optional[Any]:
        raise NotImplementedError

    def get_user_by_email(self, email: str) -> Optional[Any]:
        raise NotImplementedError

    def authenticate_user(self, username: str, password: str) -> Optional[Any]:
        raise NotImplementedError
    
    def update_user(self, user_id: UUID, **kwargs) -> Optional[Any]:
        raise NotImplementedError
    
    def delete_user(self, user_id: UUID) -> bool:
        raise NotImplementedError
    
    def authenticate_user(self, username: str, password: str) -> Optional[Any]:
        raise NotImplementedError