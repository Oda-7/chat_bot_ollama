from pydantic import BaseModel

class JWTDto(BaseModel):
    """Modèle de réponse pour le token"""
    access_token: str
    token_type: str