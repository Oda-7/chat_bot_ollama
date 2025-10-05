from pydantic import BaseModel, field_validator
from typing import Optional

from app.domain.constants.document_types import DOCUMENT_TYPE_EXTENSIONS

class DocumentUploadValidator(BaseModel):
    """Modèle de validation pour l'upload de document"""
    filename: str
    content_type: str
    file_size: int
    title: Optional[str] = None

    @field_validator('filename')
    def validate_filename(cls, v):
        if not v or not v.strip():
            raise ValueError('Le nom de fichier ne peut pas être vide')
        if len(v.strip()) > 255:
            raise ValueError('Le nom de fichier ne peut pas dépasser 255 caractères')
        return v.strip()

    @field_validator('content_type')
    def validate_content_type(cls, v):
        if not v or not v.strip():
            raise ValueError('Le type de contenu ne peut pas être vide')
         
        if v not in DOCUMENT_TYPE_EXTENSIONS:
            raise ValueError(f'Type de fichier non supporté: {v}')
        return v

    @field_validator('file_size')
    def validate_file_size(cls, v):
        max_size_mb = 50  
        if v <= 0:
            raise ValueError('La taille du fichier doit être positive')
        if v > max_size_mb * 1024 * 1024:
            raise ValueError(f'La taille du fichier ne peut pas dépasser {max_size_mb} MB')
        return v

    @field_validator('title')
    def validate_title(cls, v):
        if v and len(v.strip()) > 100:
            raise ValueError('Le titre ne peut pas dépasser 100 caractères')
        return v.strip() if v else v