from pydantic import BaseModel, Field
from datetime import datetime
from app.domains.messages.models import MessageType, MessageRole


class MessageCreate(BaseModel):
    model_id: str = Field(description="The ID of the language model to use")
    message: str = Field(description="The message to send to the language model")
    attachments: list[str] | None = Field(description="The IDs of the attachments")


class MessageResponse(BaseModel):
    id: str = Field(description="The ID of the message")
    conversation_id: str = Field(description="The ID of the conversation")
    role: MessageRole = Field(description="The role of the message")
    content: str = Field(description="The content of the message")
    message_type: MessageType = Field(description="The type of the message")
    message_metadata: dict | None = Field(description="The metadata of the message")
    file_url: str | None = Field(description="The URL of the file")
    file_name: str | None = Field(description="The name of the file")
    file_size_bytes: int | None = Field(description="The size of the file in bytes")
    tools: list[str] | None = Field(description="The tools used in the message")
    created_at: datetime = Field(description="The creation time of the message")
    updated_at: datetime = Field(description="The update time of the message")