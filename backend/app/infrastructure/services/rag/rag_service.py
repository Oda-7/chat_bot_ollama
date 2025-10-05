"""
Service RAG pour l'enrichissement contextuel des réponses IA
Architecture Clean - Couche Infrastructure
"""
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
import numpy as np
import json
from app.application.dto.document.document_upload_dto import DocumentUploadDto
from app.domain.entities.document import Document
from app.domain.entities.document_chunk import DocumentChunk
from app.domain.interfaces.services.rag.i_rag_service import IRagService
from app.domain.interfaces.repositories.document.i_document_repository import IDocumentRepository
from app.domain.interfaces.repositories.document.i_document_chunk_repository import IDocumentChunkRepository

from app.core.logging import logger

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None


class RagService(IRagService):
    def __init__(
        self,
    ):
        if TIKTOKEN_AVAILABLE:
            import tiktoken
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        else:
            self.tokenizer = None
            
        self.embedding_model = None
        self.embedding_dimension = 384 
        self._model_initialized = False
        
        self.chunk_size = 500
        self.chunk_overlap = 50
        
        

    """
    Traitement complet d'un document : chunking, embeddings, stockage
    """

    async def chunk_document(
        self, 
        user_id: str,
        file_encode: str, 
        filename: str, 
        document_repository: IDocumentRepository,
        document_chunk_repository: IDocumentChunkRepository,
        file_content: bytes = None,
        content_type: str = None,
    ) -> DocumentUploadDto:
        """ Traiter un document : chunking + embeddings + stockage """
        try:
            logger.info(f"Traitement document: {filename} ")
            user_prefix = str(user_id)[:6]
            unique_filename = f"{user_prefix}_{filename}"
                      
            await self._ensure_model_loaded()
            if not self.embedding_model:
                raise ValueError("Modèle d'embedding non disponible")
            
            content = file_encode
             
            if filename.endswith('.json') or content_type == "application/json":
                content = await self._convert_json_to_text(content)
                logger.debug(f"[RAG] Contenu JSON converti: {content[:200]}...")
            
            final_content = content
            if file_content and content_type and await self._is_excel_file(content_type, filename):
                final_content = await self._convert_excel_to_text(file_content, filename)
                logger.info(f"Contenu Excel converti: {len(final_content)} caractères")
                
            chunks = await self._chunk_document(final_content)
            logger.info(f"Document découpé en {len(chunks)} chunks")
            
            embeddings = await self._generate_embeddings(chunks)
            
            document: DocumentUploadDto = Document(
                user_id=user_id,
                filename=unique_filename ,
                file_size=len(final_content.encode('utf-8')),
                content=content,
                content_preview=final_content[:200] + "..." if len(final_content) > 200 else final_content,
                chunk_count=len(chunks),
                status="processing"
            )
            document_repository.add_document(document)
            document_repository.flush()
            document_repository.refresh(document)
            logger.info(f"Document créé en base avec ID: {document.id}")
        
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = DocumentChunk(
                    document_id=document.id,
                    chunk_index=i,
                    content=chunk_text,
                    embedding=embedding.tolist(),  
                    token_count=len(self.tokenizer.encode(chunk_text))
                )
                document_chunk_repository.add_chunk(chunk)
            
            document.status = "processed"
            document_repository.commit()
            
            logger.info(f"Document {filename} traité avec succès: {len(chunks)} chunks")
            return document
            
        except Exception as e:
            document_repository.rollback()
            logger.error(f"Erreur traitement document {filename}: {e}")
            if 'document' in locals():
                document.status = "error"
            raise
    
    async def retrieve_relevant_chunks(
        self, 
        query: str, 
        user_id: str,
        db: Session,
        top_k: int = 5,
        similarity_threshold: float = 0.75
    ) -> List[Dict[str, Any]]:
        """
        Récupérer les chunks les plus pertinents pour une requête
        Utilise une approche alternative avec calcul de similarité en Python
        """
        try:
            if not query or not isinstance(query, str):
                logger.error("La requête passée à retrieve_relevant_chunks est None ou non textuelle.")
                return []
            
            await self._ensure_model_loaded()
            if not self.embedding_model:
                logger.error("Le modèle d'embedding n'est pas initialisé.")
                return []
            
            query_embedding = self.embedding_model.encode([query])[0]
            
            chunks_query = db.execute(text("""
                SELECT 
                    dc.id,
                    dc.content,
                    dc.chunk_index,
                    d.filename,
                    dc.embedding
                FROM t7_document_chunks dc
                JOIN t7_documents d ON dc.document_id = d.id
                WHERE d.user_id = :user_id
                    AND d.status = 'processed'
                    AND dc.embedding IS NOT NULL
            """), {"user_id": user_id}).fetchall()
            
            logger.info(f"Récupérés {len(chunks_query)} chunks pour l'utilisateur {user_id}")
            
            all_results = []
            for chunk in chunks_query:
                try:
                    embedding_data = chunk.embedding
                    
                    if isinstance(embedding_data, str):
                        try:
                            import json
                            embedding_data = json.loads(embedding_data)
                        except:
                            embedding_data = eval(embedding_data) if embedding_data.startswith('[') else embedding_data
                    
                    if isinstance(embedding_data, (list, tuple)):
                        chunk_embedding = np.array(embedding_data, dtype=np.float32)
                    elif hasattr(embedding_data, '__iter__') and not isinstance(embedding_data, str):
                        chunk_embedding = np.array(list(embedding_data), dtype=np.float32)
                    else:
                        logger.warning(f"Format d'embedding non reconnu pour chunk {chunk.id}: {type(embedding_data)}")
                        continue
                    
                    if len(chunk_embedding) != len(query_embedding):
                        logger.warning(f"Dimension mismatch pour chunk {chunk.id}: {len(chunk_embedding)} vs {len(query_embedding)}")
                        continue
                    
                    similarity = np.dot(query_embedding, chunk_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
                    )
                    
                    logger.info(f"Chunk {chunk.id} ({chunk.filename}): similarité={similarity:.4f} pour la requête '{query[:50]}...'")
                    
                    all_results.append({
                        "content": chunk.content,
                        "filename": chunk.filename,
                        "chunk_index": chunk.chunk_index,
                        "similarity": float(similarity)
                    })
                        
                except Exception as e:
                    logger.warning(f"Erreur calcul similarité pour chunk {chunk.id}: {e}")
                    continue
            
            if all_results:
                max_similarity = max(r["similarity"] for r in all_results)
                
                if max_similarity >= similarity_threshold:
                    effective_threshold = 0.70
                    reason = "Excellents résultats disponibles"
                elif max_similarity >= 0.60:
                    effective_threshold = 0.55
                    reason = "Bons résultats disponibles"
                elif max_similarity >= 0.45:
                    effective_threshold = 0.40
                    reason = "Résultats moyens disponibles"
                
                logger.info(f"🎯 Seuil adaptatif: {effective_threshold:.2f} (max={max_similarity:.3f}) - {reason}")
            else:
                effective_threshold = similarity_threshold
                logger.info(f"🎯 Seuil fixe: {effective_threshold:.2f}")
            
            results = [r for r in all_results if r["similarity"] >= effective_threshold]
            
            if not results and all_results:
                logger.warning(f"⚠️ Aucun résultat >= {effective_threshold:.2f}, prise des top {min(3, len(all_results))} résultats")
                results = sorted(all_results, key=lambda x: x["similarity"], reverse=True)[:3]
            
            results.sort(key=lambda x: x["similarity"], reverse=True)
            results = results[:top_k]
            
            for i, result in enumerate(results, 1):
                logger.info(f"  #{i} - {result['filename']}: similarité={result['similarity']:.4f}")
            
            logger.info(f"✅ Trouvé {len(results)}")         
            return results
        except Exception as e:
            logger.error(f"Erreur recherche vectorielle: {e}")
            return []
        
    def build_rag_context(self, chunks: List[Dict[str, Any]], max_tokens: int = 2000) -> str:
        """
        Construire le contexte RAG à partir des chunks récupérés
        """
        if not chunks:
            return ""
        
        context_parts = []
        current_tokens = 0
        
        for chunk in chunks:
            chunk_content = f"[Source: {chunk['filename']}]\n{chunk['content']}\n"
            chunk_tokens = len(self.tokenizer.encode(chunk_content))
            
            if current_tokens + chunk_tokens > max_tokens:
                break
                
            context_parts.append(chunk_content)
            current_tokens += chunk_tokens
        
        context = "\n---\n".join(context_parts)
        logger.info(f"Contexte RAG construit: {current_tokens} tokens, {len(chunks)} sources")
        
        return f"""Contexte des documents de l'utilisateur:{context} Instructions: Utilise ces informations pour enrichir ta réponse. Cite les sources quand tu utilises des informations spécifiques."""
    
        
    async def delete_document(self, document_id: str, user_id: str, db: Session) -> bool:
        """Supprimer un document et ses chunks"""
        try:
            document = db.query(Document).filter(
                Document.id == document_id,
                Document.user_id == user_id
            ).first()
            
            if not document:
                return False
            
            db.delete(document)
            db.commit()
            
            logger.info(f"Document {document_id} supprimé pour utilisateur {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur suppression document {document_id}: {e}")
            return False

    
    # ==================== Private methods ====================
        
    async def _chunk_document(self, content: str) -> List[str]:
        """Découpage intelligent du document en chunks"""
        if '\n' in content and all(len(line) < 300 for line in content.split('\n') if line.strip()):
            return [line.strip() for line in content.split('\n') if line.strip()]
        
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(self.tokenizer.encode(paragraph)) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                sentences = paragraph.split('. ')
                for sentence in sentences:
                    if len(self.tokenizer.encode(current_chunk + sentence)) < self.chunk_size:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + ". "
            else:
                if len(self.tokenizer.encode(current_chunk + paragraph)) < self.chunk_size:
                    current_chunk += "\n\n" + paragraph
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = paragraph
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
            
    async def _ensure_model_loaded(self):
        """S'assurer que le modèle d'embedding est chargé"""
        if self._model_initialized:
            return
            
        try:
            if not SENTENCE_TRANSFORMERS_AVAILABLE:
                raise ImportError("sentence-transformers non disponible")
                
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self._model_initialized = True
            logger.info("Modèle d'embedding RAG initialisé avec succès")
        except Exception as e:
            logger.info(f"Impossible d'initialiser le modèle d'embedding: {e}")
            logger.error(f"Erreur lors de l'initialisation du modèle d'embedding: {e}")
            self.embedding_model = None
            raise
    
    async def _convert_json_to_text(self, content: str) -> str:
        """Convertit un JSON de clients en texte naturel"""
        try:
            data = json.loads(content)
            lines = []
            entreprise = data.get("entreprise", "")
            for client in data.get("clients", []):
                lines.append(
                    f"{client['nom']} est un client de {entreprise} dans le secteur {client['secteur']} avec un CA de {client['ca_annuel']}."
                )
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Erreur conversion JSON: {e}")
            return content
        
    async def _convert_excel_to_text(self, file_content: bytes, filename: str) -> str:
        """Convertit un fichier Excel en texte structuré"""
        if not PANDAS_AVAILABLE:
            raise ValueError("Support Excel non disponible - pandas non installé")
        
        try:
            from io import BytesIO, StringIO
            
            try:
                buffer = BytesIO(file_content)
                excel_file = pd.ExcelFile(buffer)
                text_parts = []
                
                for sheet_name in excel_file.sheet_names:
                    df = pd.read_excel(buffer, sheet_name=sheet_name)
                    
                    for _, row in df.iterrows():
                        row_dict = row.to_dict()
                        phrase = ", ".join(f"{k}: {v}" for k, v in row_dict.items() if pd.notna(v))
                        text_parts.append(phrase)
                        
                    return "\n".join(text_parts)
                
            except Exception as excel_error:
                logger.info(f"Excel non reconnu, tentative CSV: {excel_error}")
                try:
                    text_content = file_content.decode('utf-8')
                    df = pd.read_csv(StringIO(text_content))
                    text_parts = []
                    for _, row in df.iterrows():
                        row_dict = row.to_dict()
                        phrase = ", ".join(f"{k}: {v}" for k, v in row_dict.items() if pd.notna(v))
                        text_parts.append(phrase)
                    return "\n".join(text_parts)
                except Exception as csv_error:
                    logger.error(f"Échec CSV aussi: {csv_error}")
                    raise ValueError(f"Format de fichier non supporté: {excel_error}")
            
        except Exception as e:
            logger.error(f"Erreur conversion Excel {filename}: {e}")
            raise ValueError(f"Impossible de convertir le fichier Excel: {e}")
    
    async def _is_excel_file(self, content_type: str, filename: str) -> bool:
        """Détermine si le fichier est un Excel"""
        excel_types = [
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel.sheet.macroEnabled.12'
        ]
        excel_extensions = ['.xlsx', '.xls', '.xlsm']
        
        return (content_type in excel_types or 
                any(filename.lower().endswith(ext) for ext in excel_extensions))

    async def _generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """Générer les embeddings pour une liste de textes"""
        await self._ensure_model_loaded()
        try:
            embeddings = self.embedding_model.encode(
                texts,
                batch_size=32,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            logger.error(f"Erreur génération embeddings: {e}")
            raise
    
   