"""
Endpoint de santé pour vérifier l'état de l'API
"""
from fastapi import APIRouter
from app.core.settings import settings

router = APIRouter()


@router.get("/")
async def health_check():
    """Vérification de l'état de l'API"""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": "development" if settings.DEBUG else "production"
    }


@router.get("/ping")
async def ping():
    """Simple ping pour vérifier la connectivité"""
    return {"message": "pong"}
