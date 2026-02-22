
from pydantic import BaseModel


class FileInfo(BaseModel):
    name: str
    path: str
    type: str
    size: int | None = None
    extension: str | None = None
    modified_at: str | None = None


class DirectoryListing(BaseModel):
    path: str
    items: list[FileInfo]
    total_count: int


class FileContent(BaseModel):
    path: str
    content: str
    size: int
    encoding: str = "utf-8"
