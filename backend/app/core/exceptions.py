"""
Gestion centralisée des exceptions et modèles de réponse sécurisés
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError
from typing import Dict, Any, List, Optional
import traceback
from app.core.logging import logger


class ErrorDetail(BaseModel):
    """Modèle standardisé pour les détails d'erreur"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class StandardErrorResponse(BaseModel):
    """Modèle de réponse d'erreur standardisé et sécurisé"""
    success: bool = False
    error: str
    details: List[ErrorDetail] = []
    status_code: int
    timestamp: Optional[str] = None


class AppException(HTTPException):
    """Exception personnalisée de l'application"""
    def __init__(
        self,
        status_code: int,
        error: str,
        details: List[ErrorDetail] = None,
        headers: Dict[str, Any] = None
    ):
        self.error = error
        self.details = details or []
        super().__init__(status_code=status_code, detail=error, headers=headers)


class AuthenticationError(AppException):
    """Erreur d'authentification"""
    def __init__(self, message: str = "Authentification requise"):
        super().__init__(
            status_code=401,
            error=message,
            details=[ErrorDetail(message=message, code="AUTH_REQUIRED")]
        )


class AuthorizationError(AppException):
    """Erreur d'autorisation"""
    def __init__(self, message: str = "Accès non autorisé"):
        super().__init__(
            status_code=403,
            error=message,
            details=[ErrorDetail(message=message, code="ACCESS_DENIED")]
        )


class NotFoundError(AppException):
    """Ressource non trouvée"""
    def __init__(self, resource: str = "Ressource"):
        message = f"{resource} non trouvé(e)"
        super().__init__(
            status_code=404,
            error=message,
            details=[ErrorDetail(message=message, code="NOT_FOUND")]
        )


class ValidationError(AppException):
    """Erreur de validation"""
    def __init__(self, message: str, field: str = None):
        super().__init__(
            status_code=422,
            error="Erreur de validation",
            details=[ErrorDetail(field=field, message=message, code="VALIDATION_ERROR")]
        )


class BusinessLogicError(AppException):
    """Erreur de logique métier"""
    def __init__(self, message: str):
        super().__init__(
            status_code=400,
            error=message,
            details=[ErrorDetail(message=message, code="BUSINESS_ERROR")]
        )


def create_error_response(
    status_code: int,
    error: str,
    details: List[ErrorDetail] = None
) -> JSONResponse:
    """Créer une réponse d'erreur standardisée"""
    from datetime import datetime
    
    response = StandardErrorResponse(
        success=False,
        error=error,
        details=details or [],
        status_code=status_code,
        timestamp=datetime.utcnow().isoformat()
    )
    
    return JSONResponse(
        status_code=status_code,
        content=response.dict()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Gestionnaire pour les HTTPException"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    if isinstance(exc, AppException):
        return create_error_response(
            status_code=exc.status_code,
            error=exc.error,
            details=exc.details
        )
    
    return create_error_response(
        status_code=exc.status_code,
        error=str(exc.detail) if exc.detail else "Erreur HTTP",
        details=[ErrorDetail(message=str(exc.detail), code="HTTP_ERROR")]
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Gestionnaire pour les erreurs de validation Pydantic"""
    logger.error(f"Validation Error: {exc.errors()}")
    
    details = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"]) if error["loc"] else None
        details.append(ErrorDetail(
            field=field,
            message=error["msg"],
            code=error["type"]
        ))
    
    return create_error_response(
        status_code=422,
        error="Erreur de validation des données",
        details=details
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Gestionnaire pour les exceptions générales"""
    logger.error(f"Unexpected error: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return create_error_response(
        status_code=500,
        error="Erreur interne du serveur",
        details=[ErrorDetail(message="Une erreur inattendue s'est produite", code="INTERNAL_ERROR")]
    )


class StandardSuccessResponse(BaseModel):
    """Modèle de réponse de succès standardisé"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


def create_success_response(
    message: str,
    data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Créer une réponse de succès standardisée"""
    from datetime import datetime
    
    response = StandardSuccessResponse(
        success=True,
        message=message,
        data=data,
        timestamp=datetime.utcnow().isoformat()
    )
    
    return response.dict()
