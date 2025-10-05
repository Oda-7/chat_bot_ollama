"""
Utilitaires pour l'authentification JWT avec Argon2
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.settings import settings
from app.infrastructure.database import get_db
from app.core.logging import logger


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Créer un token d'accès JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifier un mot de passe"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hasher un mot de passe"""
    return pwd_context.hash(password)


def verify_token(token: str) -> Optional[dict]:
    """Vérifier et décoder un token JWT"""
    try:
        logger.info(f"Vérification du token JWT ")
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"Erreur JWT lors du décodage: {e}")
        return None
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la vérification du token: {e}")
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Récupérer l'utilisateur actuel à partir du token JWT
    """
    
    from app.infrastructure.repositories.user.user_repository import UserRepository
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalide",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_username(username)
        
        if user is None:
            raise credentials_exception
        
        user.payload = credentials.credentials 
            
        return user
        
    except Exception:
        raise credentials_exception
