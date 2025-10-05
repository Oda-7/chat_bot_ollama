from fastapi import UploadFile, File, HTTPException, Form
from typing import Optional
from app.domain.interfaces.repositories.document.i_document_repository import IDocumentRepository
from app.domain.interfaces.repositories.document.i_document_chunk_repository import IDocumentChunkRepository
from sqlalchemy.orm import Session
from app.domain.entities.document import Document

class IDocumentService:
    async def process_document(
        self,
        user_id: str,
        document_repository: IDocumentRepository,
        document_chunk_repository: IDocumentChunkRepository,
        title: Optional[str] = Form(None),
        file: UploadFile = File(...),
    ) -> Document:
        raise NotImplementedError