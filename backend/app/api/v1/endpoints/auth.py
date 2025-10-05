"""
Endpoints d'authentification avec base de données
"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.application.commands.user.create_user_command.create_user_validator import CreateUserValidator
from app.application.queries.user.login_user_query.login_user_validator import LoginUserValidator
from app.application.queries.user.me_user_query.me_user_query import MeUserQuery, MeUserQueryHandler
from app.core.security import create_access_token, get_current_user
from app.domain.entities.user import User
from app.infrastructure.database import get_db
from app.infrastructure.repositories.user.user_repository import UserRepository
from datetime import timedelta
from app.core.settings import settings
from app.core.logging import logger
from app.application.dto.jwt.jwt_dto import JWTDto

from app.application.queries.user.login_user_query.login_user_query import (
    LoginUserQuery,
    LoginUserQueryHandler
)
from app.application.commands.user.create_user_command.create_user_command import (
    CreateUserCommand,
    CreateUserCommandHandler
)
from app.core.exceptions import (
    AuthenticationError,
    BusinessLogicError,
    create_success_response
)

router = APIRouter()

@router.post("/login", response_model=JWTDto)
async def login(user_login: LoginUserValidator, db: Session = Depends(get_db)):
    """Connexion utilisateur avec base de données"""
    try:
        user_repo = UserRepository(db)
        handler = LoginUserQueryHandler(user_repo)
        query = LoginUserQuery(
            username=user_login.username,
            password=user_login.password
        )
        user = handler.handle(query)
        
        if not user:
            logger.warning(f"Tentative de connexion échouée pour: {user_login.username}")
            raise AuthenticationError("Nom d'utilisateur ou mot de passe incorrect")
        
        if not user.is_active:
            raise BusinessLogicError("Compte utilisateur désactivé")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": str(user.id)}, 
            expires_delta=access_token_expires
        )
        
        logger.info(f"Connexion réussie pour: {user.username}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except (AuthenticationError, BusinessLogicError):
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur interne du serveur"
        )


@router.post("/register")
async def register(user_register: CreateUserValidator, db: Session = Depends(get_db)):
    """Inscription utilisateur avec base de données"""
    try:
        user_repo = UserRepository(db)
        
        handler = CreateUserCommandHandler(user_repo)
        command = CreateUserCommand(
            username=user_register.username,
            email=f"{user_register.username.lower()}@local.dev",
            password=user_register.password
        )
        user = handler.handle(command)
        
        logger.info(f"Nouvel utilisateur créé: {user.username}")
        return create_success_response(
            message="Utilisateur créé avec succès",
            data={
                "username": user.username,
                "email": user.email
            }
        )
        
    except BusinessLogicError:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la création d'utilisateur: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la création du compte"
        )

@router.get("/me", response_model=JWTDto)
async def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Récupérer les informations de l'utilisateur connecté"""
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non authentifié"
        )
    
    user_repository = UserRepository(db)
    handler = MeUserQueryHandler(user_repository)
    query = MeUserQuery(user_id=str(current_user.id))
    
    user = handler.handle(query)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé"
        )

    return {"access_token": current_user.payload, "token_type": "bearer"}
