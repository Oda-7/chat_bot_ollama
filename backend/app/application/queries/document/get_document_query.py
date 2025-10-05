from typing import List
from uuid import UUID

from app.domain.interfaces.repositories.document.i_document_repository import IDocumentRepository
from app.domain.entities.document import Document


class GetDocumentQuery:
    def __init__(self,  user_id: UUID):
        self.user_id = user_id

class GetDocumentQueryHandler:
    def __init__(self, document_repository: IDocumentRepository):
        self.document_repository = document_repository

    async def handle(self, query: GetDocumentQuery) -> List[Document]:
        """Récupérer tous les documents d'un utilisateur"""
        documents: List[Document] = self.document_repository.get_all_documents(query.user_id)
        
        if not documents:
            return []

        return documents