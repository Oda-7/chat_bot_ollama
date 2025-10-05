"""
Configuration settings pour l'application ChatBot
Utilise Pydantic Settings pour la gestion de la configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configuration principale de l'application"""
    
    APP_NAME: str = "ChatBot API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API pour ChatBot avec Ollama et RAG"
    DEBUG: bool = False
    
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    RELOAD: bool = True
    
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    DATABASE_URL: str = "postgresql://chatbot_user:chatbot_password@localhost:5432/chatbot_db"
    DATABASE_URL_ASYNC: str = "postgresql+asyncpg://chatbot_user:chatbot_password@localhost:5432/chatbot_db"
    
    OLLAMA_BASE_URL: str = "http://localhost:11434" 
    OLLAMA_MODEL: str = "mistral:7b"
    
    CHROMA_DB_PATH: str = "./chroma_db"
    EMBEDDINGS_MODEL: str = "all-MiniLM-L6-v2"
    
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
