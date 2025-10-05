from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.domain.entities.document import Document
from app.domain.interfaces.repositories.document.i_document_repository import IDocumentRepository

class DocumentRepository(IDocumentRepository):
    def __init__(self, db: Session):
        self.db = db
        
    def commit(self):
        self.db.commit()
        
    def refresh(self, document: Document):
        self.db.refresh(document)
        
    def flush(self):
        self.db.flush()

    def add_document(self, document: Document) -> Document:
        self.db.add(document)
        self.db.flush()
        self.db.refresh(document)
        return document

    def get_document_by_id(self, document_id: int) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def get_document_by_filename(self, filename: str) -> Optional[Document]:
        return self.db.query(Document).filter(Document.filename == filename).first()

    def get_all_documents(self, user_id: UUID) -> List[Document]:
        return self.db.query(Document).filter(Document.user_id == user_id).all()

    def update_document(self, document: Document) -> Document:
        self.db.merge(document)
        self.db.flush()
        return document

    def delete_document(self, document_id: int) -> None:
        document = self.get_document_by_id(document_id)
        if document:
            self.db.delete(document)
            self.db.flush()
            
    def rollback(self):
        self.db.rollback()