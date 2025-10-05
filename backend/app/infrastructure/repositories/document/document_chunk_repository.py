from app.domain.entities.document_chunk import DocumentChunk
from app.domain.interfaces.repositories.document.i_document_chunk_repository import IDocumentChunkRepository
from sqlalchemy.orm import Session

class DocumentChunkRepository(IDocumentChunkRepository):
    def __init__(self, db: Session):
        self.db = db

    def add_chunk(self, chunk: DocumentChunk) -> None:
        self.db.add(chunk)
        self.db.commit()

    def get_chunks_by_document_id(self, document_id: str) -> list[DocumentChunk]:
        return self.db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()

    def get_chunk_by_id(self, chunk_id: str) -> DocumentChunk | None:
        return self.db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()

    def delete_chunk(self, chunk_id: str) -> None:
        chunk = self.get_chunk_by_id(chunk_id)
        if chunk:
            self.db.delete(chunk)
            self.db.commit()

    def delete_chunks_by_document_id(self, document_id: str) -> None:
        chunks = self.get_chunks_by_document_id(document_id)
        for chunk in chunks:
            self.db.delete(chunk)
        self.db.commit()