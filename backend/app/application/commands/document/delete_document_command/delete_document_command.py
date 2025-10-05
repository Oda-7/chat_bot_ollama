from app.domain.interfaces.repositories.document.i_document_chunk_repository import IDocumentChunkRepository
from app.domain.interfaces.repositories.document.i_document_repository import IDocumentRepository

class DeleteDocumentCommand:
    def __init__(self, document_id: int):
        self.document_id = document_id
        
class DeleteDocumentCommandHandler:
    def __init__(self, document_repository: IDocumentRepository, document_chunk_repository: IDocumentChunkRepository):
        self.document_repository = document_repository
        self.document_chunk_repository = document_chunk_repository

    async def handle(self, command: DeleteDocumentCommand) -> bool:
        """Supprimer un document et ses chunks"""
        document = self.document_repository.get_document_by_id(
            document_id=command.document_id,
        )
        if not document:
            return False  

        self.document_repository.delete_document(document_id=command.document_id)
        self.document_chunk_repository.delete_chunks_by_document_id(document_id=command.document_id)
        return True