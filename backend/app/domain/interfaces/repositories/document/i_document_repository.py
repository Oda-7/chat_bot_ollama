from typing import Optional
from app.domain.entities.document import Document
from uuid import UUID


class IDocumentRepository:
    """ Interface for document repository operations. """
    def commit(self):
        raise NotImplementedError
    
    def refresh(self, document: Document) -> Document:
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def add_document(self, document: Document) -> Document:
        raise NotImplementedError

    def get_document_by_id(self, document_id: UUID) -> Optional[Document]:
        raise NotImplementedError

    def get_document_by_filename(self, filename: str) -> Optional[Document]:
        raise NotImplementedError

    def get_all_documents(self) -> list[Document]:
        raise NotImplementedError

    def update_document(self, document_id: UUID, document: Document) -> Optional[Document]:
        raise NotImplementedError

    def delete_document(self, document_id: UUID) -> bool:
        raise NotImplementedError
    
    def rollback(self):
        raise NotImplementedError