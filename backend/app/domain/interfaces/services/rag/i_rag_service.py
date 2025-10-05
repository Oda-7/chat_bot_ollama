from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.domain.interfaces.repositories.document.i_document_chunk_repository import IDocumentChunkRepository

class IRagService:
    async def chunk_document(
        self, 
        document_chunk_repository: IDocumentChunkRepository,
        docuement_repository: IDocumentChunkRepository,
        content: str, 
        filename: str, 
        file_content: bytes = None,
        content_type: str = None
    ):
        raise NotImplementedError

    async def retrieve_relevant_chunks(
        self, 
        query: str, 
        user_id: str,
        db: Session,
        top_k: int = 5,
        similarity_threshold: float = 0.65
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def build_rag_context(
        self, 
        chunks: List[Dict[str, Any]], 
        max_tokens: int = 2000
    ) -> str:
        raise NotImplementedError

    async def get_user_documents(
        self, 
        user_id: str, 
        db: Session
    ):
        raise NotImplementedError

    async def delete_document(
        self, 
        document_id: str, 
        user_id: str, 
        db: Session
    ) -> bool:
        raise NotImplementedError