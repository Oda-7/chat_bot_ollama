from typing import Optional
from fastapi import UploadFile, File, Form
from app.application.dto.document.document_upload_response_dto import DocumentUploadResponseDto
from app.domain.interfaces.repositories.document.i_document_repository import IDocumentRepository
from app.domain.interfaces.repositories.document.i_document_chunk_repository import IDocumentChunkRepository
from app.application.dto.document.document_upload_dto import DocumentUploadDto
from app.domain.entities.user import User
from app.domain.interfaces.services.document.i_document_service import IDocumentService
from app.infrastructure.services.document.document_service import DocumentService

class DocumentUploadCommand:
    def __init__(self, current_user: User, file: UploadFile = File(...), title: Optional[str] = Form(None)):
        self.current_user = current_user
        self.file = file
        self.title = title
        
class DocumentUploadCommandHandler: 
    def __init__(
        self,
        document_repository: IDocumentRepository,
        document_chunk_repository: IDocumentChunkRepository,
    ):
        self.document_repository = document_repository
        self.document_chunk_repository = document_chunk_repository

    async def handle(self, command: DocumentUploadCommand) -> DocumentUploadDto:
        try:
            if not command.file.filename:
                raise ValueError("Nom de fichier manquant")

            document_service: IDocumentService = DocumentService(
                document_repository=self.document_repository,
                document_chunk_repository=self.document_chunk_repository
            )
            document: DocumentUploadDto = await document_service.process_document(
                user_id=command.current_user.id,
                title=command.title,
                file=command.file
            )
            
            return DocumentUploadResponseDto(
                id=document.id,
                filename=document.filename,
                file_size=document.file_size,
                status=document.status,
                message="Document uploadé avec succès",
            ) 
        except Exception as e:
            raise e