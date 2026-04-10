from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.domains.messages.models import MessageType, MessageRole


class MessageCreate(BaseModel):
    model_id: str = Field(description="The ID of the language model to use")
    message: str = Field(description="The message to send to the language model")
    attachments: list[str] | None = Field(description="The IDs of the attachments")
    image_model_id: Optional[str] = Field(default=None, description="The ID of the image model to use")


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

    model_config = ConfigDict(from_attributes=True)


class StreamDoneEvent(BaseModel):
    """Payload for the SSE 'done' event after streaming completes."""
    message_id: str = Field(description="The ID of the saved assistant message")
    conversation_id: str = Field(description="The ID of the conversation")
    content: str = Field(description="The full accumulated response content")
    role: MessageRole = Field(default=MessageRole.ASSISTANT)
    message_type: MessageType = Field(default=MessageType.TEXT)
    tools_used: list[str] = Field(default_factory=list, description="Tools that were called during generation")