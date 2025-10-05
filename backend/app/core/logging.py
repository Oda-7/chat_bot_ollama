"""
Configuration de logging avec Loguru
"""
import sys
from loguru import logger
from app.core.settings import settings


def setup_logging():
    """Configuration du système de logging"""
    
    logger.remove()

    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True
    )
    
    logger.add(
        "/app/logs/app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG"
    )
    
    logger.add(
        "logs/errors_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    return logger

logger = setup_logging()
