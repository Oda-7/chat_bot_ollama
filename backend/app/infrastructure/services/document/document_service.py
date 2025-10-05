from fastapi import UploadFile, File, HTTPException
from typing import List, Optional

from requests import Session
from app.application.commands.document.document_upload_command.document_upload_validator import DocumentUploadValidator
from app.application.dto.document.document_upload_dto import DocumentUploadDto
from app.domain.interfaces.repositories.document.i_document_repository import (
    IDocumentRepository,
)
from app.domain.interfaces.repositories.document.i_document_chunk_repository import (
    IDocumentChunkRepository,
)
from app.domain.interfaces.services.document.i_document_service import IDocumentService
from app.domain.interfaces.services.rag.i_rag_service import IRagService

from app.core.logging import logger
import mimetypes
from app.infrastructure.services.rag.rag_service import RagService


class DocumentService(IDocumentService):
    def __init__(
        self,
        document_repository: IDocumentRepository,
        document_chunk_repository: IDocumentChunkRepository,
    ):
        self.document_repository = document_repository
        self.document_chunk_repository = document_chunk_repository

    async def process_document(
        self,
        user_id: str,
        title: Optional[str],
        file: UploadFile = File(...),
    )-> DocumentUploadDto:
        """Processus complet de gestion d'un document uploadé."""
        logger.info(f"Traitement document: {file.filename} pour utilisateur {user_id}")

        existing_document = self.document_repository.get_document_by_filename(
            file.filename
        )
        if existing_document:
            raise ValueError("Un document avec ce nom existe déjà")

        content_bytes = await file.read()
        content_type = file.content_type or mimetypes.guess_type(file.filename)[0]
        
        DocumentUploadValidator(
            filename=file.filename,
            content_type=content_type,
            file_size=len(content_bytes),
            title=title,
        )

        is_excel = content_type in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel.sheet.macroEnabled.12",
        ]

        encode_file = ""
        if not is_excel:
            try:
                encode_file = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    encode_file = content_bytes.decode("latin-1")
                except UnicodeDecodeError:
                    raise HTTPException(
                        status_code=400, detail="Encodage de fichier non supporté"
                    )

            if len(encode_file.strip()) < 100:
                raise HTTPException(
                    status_code=400, detail="Contenu du fichier trop court"
                )

        rag_service: IRagService = RagService()
        document: DocumentUploadDto = await rag_service.chunk_document(
            user_id=user_id,
            file_encode=encode_file,
            filename=file.filename,
            document_repository=self.document_repository,
            document_chunk_repository=self.document_chunk_repository,
            file_content=content_bytes,
            content_type=content_type,
        )

        return document