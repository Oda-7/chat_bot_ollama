from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class DocumentInfoResponseDto(BaseModel):
    """Modèle d'information document"""

    id: UUID
    filename: str
    content_preview: Optional[str]
    file_size: int
    chunk_count: int
    status: str
    created_at: str