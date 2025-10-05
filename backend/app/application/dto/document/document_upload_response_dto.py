from uuid import UUID
from pydantic import BaseModel

class DocumentUploadResponseDto(BaseModel):
    id: UUID
    filename: str
    file_size: int
    status: str
    message: str