from pydantic import BaseModel, field_validator


class LoginUserValidator(BaseModel):
    """Modèle pour la connexion utilisateur"""
    username: str
    password: str
    
    @field_validator('username')
    def username_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Le nom d\'utilisateur ne peut pas être vide')
        if len(v.strip()) < 3:
            raise ValueError('Le nom d\'utilisateur doit contenir au moins 3 caractères')
        return v.strip()
    
    @field_validator('password')
    def password_must_not_be_empty(cls, v):
        if not v:
            raise ValueError('Le mot de passe ne peut pas être vide')
        if len(v) < 6:
            raise ValueError('Le mot de passe doit contenir au moins 6 caractères')
        return v