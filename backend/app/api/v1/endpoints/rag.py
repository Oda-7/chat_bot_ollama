"""
Endpoints pour la gestion des documents RAG
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.application.commands.document.delete_document_command.delete_document_command import DeleteDocumentCommand, DeleteDocumentCommandHandler
from app.application.commands.document.document_upload_command.document_upload_command import (
    DocumentUploadCommand,
    DocumentUploadCommandHandler,
)
from app.application.dto.document.document_info_response import DocumentInfoResponseDto
from app.application.queries.document.get_document_query import GetDocumentQuery, GetDocumentQueryHandler
from app.infrastructure.repositories.document.document_repository import (
    DocumentRepository,
)
from app.infrastructure.repositories.document.document_chunk_repository import (
    DocumentChunkRepository,
)
from app.application.dto.document.document_upload_response_dto import (
    DocumentUploadResponseDto,
)
from app.infrastructure.database import get_db
from app.core.security import get_current_user
from app.domain.entities.user import User
from app.core.logging import logger
from app.infrastructure.services.rag.rag_service import RagService

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponseDto)
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload un document pour indexation RAG
    """
    try:
        logger.info(f"Début upload: {file.filename} par {current_user.username}")

        document_repository = DocumentRepository(db)
        chunk_repository = DocumentChunkRepository(db)

        handler = DocumentUploadCommandHandler(
            document_repository=document_repository, document_chunk_repository=chunk_repository
        )
        command = DocumentUploadCommand(
            current_user=current_user,
            title=title,
            file=file
        )

        document: DocumentUploadResponseDto = await handler.handle(command)
        logger.info(f"Document {file.filename} uploadé par {current_user.username}")

        return document
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur upload document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du traitement du document",
        )


@router.get("/documents", response_model=List[DocumentInfoResponseDto])
async def get_user_documents(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Récupérer tous les documents de l'utilisateur
    """
    try:
        document_repository = DocumentRepository(db)
        handler = GetDocumentQueryHandler(document_repository=document_repository)
        query = GetDocumentQuery(user_id=current_user.id)
        
        documents = await handler.handle(query)

        return [
            DocumentInfoResponseDto(
                id=doc.id,
                filename=doc.filename,
                content_preview=doc.content_preview,
                file_size=doc.file_size,
                chunk_count=doc.chunk_count,
                status=doc.status,
                created_at=doc.created_at.isoformat(),
            )
            for doc in documents
        ]
    except Exception as e:
        logger.error(f"Erreur récupération documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la récupération des documents",
        )


@router.post("/search")
async def search_documents(
    query: str = Form(...),
    top_k: int = Form(5),
    similarity_threshold: float = Form(0.7),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Rechercher dans les documents de l'utilisateur
    """
    try:
        rag_service = RagService()

        results = await rag_service.retrieve_relevant_chunks(
            query=query,
            user_id=current_user.id,
            db=db,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
        )

        return {"query": query, "results": results, "count": len(results)}

    except Exception as e:
        logger.error(f"Erreur recherche documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la recherche",
        )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Supprimer un document et ses chunks
    """
    try:
        document_repository = DocumentRepository(db)
        document_chunk_repository = DocumentChunkRepository(db)
        handler = DeleteDocumentCommandHandler(document_repository=document_repository, document_chunk_repository=document_chunk_repository)
        command = DeleteDocumentCommand(
            document_id=document_id
        )

        success = await handler.handle(command)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document non trouvé"
            )

        return {"message": "Document supprimé avec succès"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur suppression document {document_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression du document",
        )
