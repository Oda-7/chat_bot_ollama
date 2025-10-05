from typing import List
from sqlalchemy.orm import Session
from app.domain.entities.document_chunk import DocumentChunk

class IDocumentChunkRepository:
    """Contrat d'accès aux chunks de document RAG"""

    def add_chunk(self, chunk: DocumentChunk, db: Session) -> DocumentChunk:
        raise NotImplementedError

    def get_chunks_by_document(self, document_id: str, db: Session) -> List[DocumentChunk]:
        raise NotImplementedError

    def get_chunks_by_user(self, user_id: str, db: Session) -> List[DocumentChunk]:
        raise NotImplementedError

    def search_chunks(self, user_id: str, query_embedding, top_k: int, similarity_threshold: float, db: Session) -> List[DocumentChunk]:
        raise NotImplementedError
    
    def delete_chunks_by_document_id(self, document_id: str, db: Session) -> None:
        raise NotImplementedError