
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    path: str = Field(min_length=1)
    description: str | None = Field(None, max_length=500)


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class Project(BaseModel):
    id: str
    name: str
    path: str
    description: str | None
    created_at: str
    conversation_count: int = 0
