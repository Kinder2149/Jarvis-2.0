from pydantic import BaseModel

class PostBase(BaseModel):
    """Modèle de base pour un post, avec titre et contenu."""
    title: str
    content: str

class PostCreate(PostBase):
    """Modèle utilisé pour la création d'un post (pas d'ID requis)."""
    pass

class Post(PostBase):
    """Modèle complet d'un post, incluant son ID."""
    id: int

    class Config:
        """Configuration Pydantic pour permettre le mode ORM."""
        from_attributes = True
