from fastapi import FastAPI, HTTPException, status
from typing import List
from . import models
from . import database

app = FastAPI(
    title="Mini-Blog API",
    description="Une API simple pour gérer des posts de blog.",
    version="1.0.0"
)

@app.post("/posts", response_model=models.Post, status_code=status.HTTP_201_CREATED)
def create_post(post: models.PostCreate):
    """
    Crée un nouveau post.
    """
    new_id = database.get_next_id()
    new_post = models.Post(id=new_id, title=post.title, content=post.content)
    database.db.append(new_post.model_dump())
    return new_post

@app.get("/posts", response_model=List[models.Post])
def get_all_posts():
    """
    Récupère la liste de tous les posts.
    """
    return database.db

@app.get("/posts/{post_id}", response_model=models.Post)
def get_post_by_id(post_id: int):
    """
    Récupère un post spécifique par son ID.
    """
    if not isinstance(post_id, int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'ID du post doit être un entier."
        )
    
    post = next((p for p in database.db if p["id"] == post_id), None)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le post avec l'ID {post_id} n'a pas été trouvé."
        )
    return post

@app.put("/posts/{post_id}", response_model=models.Post)
def update_post(post_id: int, updated_post: models.PostCreate):
    """
    Met à jour un post existant.
    """
    if not isinstance(post_id, int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'ID du post doit être un entier."
        )

    post_index = -1
    for i, p in enumerate(database.db):
        if p["id"] == post_id:
            post_index = i
            break
            
    if post_index == -1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le post avec l'ID {post_id} n'a pas été trouvé."
        )
    
    post = database.db[post_index]
    post["title"] = updated_post.title
    post["content"] = updated_post.content
    
    return post

@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    """
    Supprime un post par son ID.
    """
    if not isinstance(post_id, int):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'ID du post doit être un entier."
        )
        
    post_to_delete = next((p for p in database.db if p["id"] == post_id), None)
    
    if post_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Le post avec l'ID {post_id} n'a pas été trouvé."
        )
        
    database.db.remove(post_to_delete)
    return
