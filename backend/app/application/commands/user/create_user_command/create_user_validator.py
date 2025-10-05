from pydantic import BaseModel, field_validator

class CreateUserValidator(BaseModel):
    """Modèle pour l'inscription utilisateur"""
    username: str
    password: str
    
    @field_validator('username')
    def validate_username(cls, v):
        if not v or not v.strip():
            raise ValueError('Le nom d\'utilisateur ne peut pas être vide')
        if len(v.strip()) < 3:
            raise ValueError('Le nom d\'utilisateur doit contenir au moins 3 caractères')
        if len(v.strip()) > 50:
            raise ValueError('Le nom d\'utilisateur ne peut pas dépasser 50 caractères')
        
        return v.strip()
    
    @field_validator('password')
    def validate_password(cls, v):
        if not v:
            raise ValueError('Le mot de passe ne peut pas être vide')
        if len(v) < 6:
            raise ValueError('Le mot de passe doit contenir au moins 6 caractères')
        if len(v) > 100:
            raise ValueError('Le mot de passe ne peut pas dépasser 100 caractères')
        return v