from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DocumentUploadDto(BaseModel):
    id: UUID
    user_id: UUID
    filename: str
    file_size: int
    content: str
    content_preview: Optional[str]
    chunk_count: int
    status: str
    created_at: datetime