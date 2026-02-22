"""
Template — API REST Mini-Blog avec FastAPI
API REST complète pour gérer des articles de blog
"""

from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Modèles Pydantic
class ArticleBase(BaseModel):
    title: str
    content: str
    author: str


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    author: str | None = None


class Article(ArticleBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Stockage en mémoire (remplacer par une vraie DB en production)
articles_db: list[Article] = []
next_id = 1


# Application FastAPI
app = FastAPI(
    title="Mini-Blog API", description="API REST pour gérer des articles de blog", version="1.0.0"
)


@app.get("/")
def read_root():
    """Page d'accueil de l'API"""
    return {
        "message": "Bienvenue sur l'API Mini-Blog",
        "endpoints": {
            "GET /articles": "Liste tous les articles",
            "GET /articles/{id}": "Récupère un article par ID",
            "POST /articles": "Crée un nouvel article",
            "PUT /articles/{id}": "Met à jour un article",
            "DELETE /articles/{id}": "Supprime un article",
        },
    }


@app.get("/articles", response_model=list[Article])
def get_articles():
    """Liste tous les articles"""
    return articles_db


@app.get("/articles/{article_id}", response_model=Article)
def get_article(article_id: int):
    """Récupère un article par son ID"""
    for article in articles_db:
        if article.id == article_id:
            return article
    raise HTTPException(status_code=404, detail="Article non trouvé")


@app.post("/articles", response_model=Article, status_code=201)
def create_article(article: ArticleCreate):
    """Crée un nouvel article"""
    global next_id

    now = datetime.now()
    new_article = Article(
        id=next_id,
        title=article.title,
        content=article.content,
        author=article.author,
        created_at=now,
        updated_at=now,
    )

    articles_db.append(new_article)
    next_id += 1

    return new_article


@app.put("/articles/{article_id}", response_model=Article)
def update_article(article_id: int, article_update: ArticleUpdate):
    """Met à jour un article existant"""
    for article in articles_db:
        if article.id == article_id:
            if article_update.title is not None:
                article.title = article_update.title
            if article_update.content is not None:
                article.content = article_update.content
            if article_update.author is not None:
                article.author = article_update.author

            article.updated_at = datetime.now()
            return article

    raise HTTPException(status_code=404, detail="Article non trouvé")


@app.delete("/articles/{article_id}", status_code=204)
def delete_article(article_id: int):
    """Supprime un article"""
    for i, article in enumerate(articles_db):
        if article.id == article_id:
            articles_db.pop(i)
            return

    raise HTTPException(status_code=404, detail="Article non trouvé")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
