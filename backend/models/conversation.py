
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    agent_id: str = Field(pattern="^(BASE|JARVIS_Maître)$")
    title: str | None = Field(None, max_length=200)


class Conversation(BaseModel):
    id: str
    project_id: str | None
    agent_id: str
    title: str | None
    created_at: str
    updated_at: str
    message_count: int = 0


class Message(BaseModel):
    id: int
    conversation_id: str
    role: str
    content: str
    timestamp: str


class ChatMessage(BaseModel):
    content: str = Field(min_length=1, max_length=10_000)
