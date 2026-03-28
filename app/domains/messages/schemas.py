from pydantic import BaseModel
from datetime import datetime

class MessageCreate(BaseModel):
    model: str
    message: str


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    message_type: str
    message_metadata: dict | None
    file_url: str | None
    file_name: str | None
    file_size_bytes: int | None
    tools: list[str] | None
    created_at: datetime
    updated_at: datetime