"""
Point d'entrée pour démarrer l'application FastAPI
Compatible développement local et Docker
"""
import uvicorn
import os
from app.core.settings import settings

if __name__ == "__main__":
    host = os.getenv("HOST", settings.HOST)
    port = int(os.getenv("PORT", settings.PORT))
    
    if os.getenv("DOCKER_ENV"):
        host = "0.0.0.0"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=settings.RELOAD and not os.getenv("DOCKER_ENV"), 
        log_level="info",
        access_log=True
    )
