from pydantic import BaseModel
from datetime import datetime, timezone


class ConversationCreate(BaseModel):
    title: str = "New Conversation"


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    pinned: bool
    created_at: datetime
    updated_at: datetime




    