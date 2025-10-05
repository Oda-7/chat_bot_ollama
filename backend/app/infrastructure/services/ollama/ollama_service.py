"""
Service Ollama pour l'intégration IA
Architecture Clean - Couche Infrastructure
"""
import time
from typing import Optional, Dict, Any, List
import httpx
import ollama
from app.core.settings import settings
from app.core.logging import logger


class OllamaService:
    """Service pour communiquer avec Ollama"""
    
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_MODEL
        self.client = ollama.Client(host=self.base_url)
    
    async def is_ollama_available(self) -> bool:
        """Vérifier si Ollama est disponible"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/version", timeout=5.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama non disponible: {e}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Lister les modèles disponibles"""
        try:
            models = self.client.list()
            return models.get('models', [])
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des modèles: {e}")
            return []
    
    async def pull_model(self, model_name: str) -> bool:
        """Télécharger un modèle si nécessaire"""
        try:
            logger.info(f"Téléchargement du modèle {model_name}...")
            self.client.pull(model_name)
            logger.info(f"Modèle {model_name} téléchargé avec succès")
            return True
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement du modèle {model_name}: {e}")
            return False
    
    async def generate_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        system_message: Optional[str] = None,
        context: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Générer une réponse avec Ollama
        
        Args:
            prompt: Le prompt utilisateur
            model: Modèle à utiliser (défaut: settings.OLLAMA_MODEL)
            system_message: Message système pour définir le comportement
            context: Contexte RAG optionnel
            max_tokens: Nombre maximum de tokens
            temperature: Créativité (0.0 = déterministe, 1.0 = créatif)
        
        Returns:
            Dict contenant la réponse et les métadonnées
        """
        model = model or self.default_model
        
        try:
            final_prompt = self._build_prompt(prompt, system_message, context)
            
            logger.info(f"Génération avec {model}: {prompt[:50]}...")
            
            import time
            start_time = time.time()
            
            response = self.client.generate(
                model=model,
                prompt=final_prompt,
                options={
                    'num_predict': max_tokens,
                    'temperature': temperature,
                    'top_p': 0.9,
                    'stop': ['</s>', '<|end|>']
                }
            )
            
            end_time = time.time()
            response_time = int((end_time - start_time) * 1000)  
            
            logger.info(f"Réponse générée en {response_time}ms")
            
            return {
                'response': response['response'].strip(),
                'model': model,
                'response_time': response_time,
                'tokens_used': len(response['response'].split()),  
                'success': True,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération avec {model}: {e}")
            return {
                'response': f"Désolé, une erreur est survenue lors de la génération de la réponse.",
                'model': model,
                'response_time': 0,
                'tokens_used': 0,
                'success': False,
                'error': str(e)
            }
    
    def _build_prompt(
        self, 
        user_prompt: str, 
        system_message: Optional[str] = None,
        context: Optional[str] = None
    ) -> str:
        """Construire le prompt final avec système et contexte"""
        
        parts = []
        
        default_system = """Tu es un assistant IA serviable, précis et professionnel. 
Réponds de manière claire et concise en français."""
        
        system = system_message or default_system
        parts.append(f"System: {system}")
        
        if context:
            parts.append(f"Contexte: {context}")
        
        parts.append(f"Human: {user_prompt}")
        parts.append("Assistant:")
        
        return "\n\n".join(parts)
    
    async def generate_stream_response(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        system_message: Optional[str] = None,
        context: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ):
        """
        Générer une réponse en streaming avec Ollama
        """

        start_time = time.time()
        try:
            model = model or self.default_model
            logger.info(f"Streaming avec {model}: {prompt[:50]}...")
            final_prompt = self._build_prompt(prompt, system_message, context)
        
            for chunk in self.client.generate(
                model=model,
                prompt=final_prompt,
                options={
                    'num_predict': max_tokens,
                    'temperature': temperature,
                    'top_p': 0.9,
                    'stop': ['</s>', '<|end|>']
                },
                stream=True
            ):
                yield chunk['response']
            end_time = time.time()
            logger.info(f"Streaming terminé en {int((end_time - start_time) * 1000)}ms")
        except Exception as e:
            logger.error(f"Erreur streaming Ollama: {e}")
            yield f"[ERREUR] {str(e)}"
