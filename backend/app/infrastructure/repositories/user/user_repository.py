from sqlalchemy.orm import Session
from typing import Optional
from app.domain.entities.user import User
from app.domain.interfaces.repositories.user.i_user_repository import IUserRepository
from uuid import UUID

class UserRepository(IUserRepository):
    """Repository pour la gestion des utilisateurs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(
        self, 
        username: str, 
        email: str,
        password: str, 
    ) -> User:
        """Créer un nouvel utilisateur"""
        from app.core.security import get_password_hash
        
        hashed_password = get_password_hash(password)
        
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Récupérer un utilisateur par nom d'utilisateur"""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Récupérer un utilisateur par email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Récupérer un utilisateur par ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authentifier un utilisateur"""
        from app.core.security import verify_password
        
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def update_user(self, user_id: UUID, **kwargs) -> Optional[User]:
        """Mettre à jour un utilisateur"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete_user(self, user_id: UUID) -> bool:
        """Supprimer un utilisateur"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        return True