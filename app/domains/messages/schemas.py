from pydantic import BaseModel
from datetime import datetime
from app.domains.messages.models import MessageType, MessageRole

class MessageCreate(BaseModel):
    model_id: str
    message: str


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: MessageRole
    content: str
    message_type: MessageType
    message_metadata: dict | None
    file_url: str | None
    file_name: str | None
    file_size_bytes: int | None
    tools: list[str] | None
    created_at: datetime
    updated_at: datetime