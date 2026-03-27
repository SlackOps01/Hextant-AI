from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ConversationCreate(BaseModel):
    title: str = Field(default="New Conversation", max_length=255, description="Title of the conversation")


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    title: str
    pinned: bool
    created_at: datetime
    updated_at: datetime

class ConversationUpdate(BaseModel):
    title: str
    




    