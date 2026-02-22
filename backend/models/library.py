
from pydantic import BaseModel, Field


class LibraryDocument(BaseModel):
    id: str
    category: str
    name: str
    icon: str | None = None
    description: str
    content: str
    tags: list[str]
    agents: list[str]
    created_at: str
    updated_at: str


class LibraryDocumentCreate(BaseModel):
    category: str = Field(pattern=r"^(libraries|methodologies|prompts|personal)$")
    name: str = Field(min_length=1, max_length=200)
    icon: str | None = Field(default=None, max_length=10)
    description: str = Field(min_length=1, max_length=500)
    content: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list)
    agents: list[str] = Field(default_factory=list)


class LibraryDocumentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    icon: str | None = Field(default=None, max_length=10)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    content: str | None = Field(default=None, min_length=1)
    tags: list[str] | None = None
    agents: list[str] | None = None
