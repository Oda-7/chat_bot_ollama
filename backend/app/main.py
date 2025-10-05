"""
Application FastAPI principale
Configuration avec CORS, middleware et routing
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from app.core.settings import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
import os

logger = setup_logging()
os.makedirs("logs", exist_ok=True)
logger.debug("TEST LOGURU: Démarrage backend, test création fichier log du jour.")


def create_application() -> FastAPI:
    """Factory pour créer l'application FastAPI"""
    
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        websockets_ping_interval=20,  
        websockets_ping_timeout=20   
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(api_router, prefix="/api/v1")
    
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    return app


app = create_application()


@app.on_event("startup")
async def startup_event():
    """Événements au démarrage de l'application"""
    logger.info(f"🚀 Démarrage de {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"📚 Documentation disponible sur: http://{settings.HOST}:{settings.PORT}/api/docs")
    logger.info(f"📖 ReDoc disponible sur: http://{settings.HOST}:{settings.PORT}/api/redoc")
    logger.info(f"🌐 API accessible sur: http://{settings.HOST}:{settings.PORT}/api/v1")


@app.on_event("shutdown")
async def shutdown_event():
    """Événements à l'arrêt de l'application"""
    logger.info("🛑 Arrêt de l'application")


@app.get("/")
async def root():
    """Route racine avec informations sur l'API"""
    return {
        "message": f"Bienvenue sur {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs_url": "/api/docs",
        "redoc_url": "/api/redoc"
    }

