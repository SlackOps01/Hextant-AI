from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class AttachmentResponse(BaseModel):
    id: str = Field(description="The ID of the attachment")
    s3_key: str = Field(description="The S3 key of the attachment")
    file_name: str = Field(description="The original file name")
    file_size_bytes: int = Field(description="The size of the file in bytes")
    mime_type: str | None = Field(default=None, description="The MIME type of the file")
    message_id: str | None = Field(
        default=None, description="The ID of the linked message"
    )
    created_at: datetime = Field(description="The creation time of the attachment")

    model_config = ConfigDict(from_attributes=True)


class PresignedUrlResponse(BaseModel):
    url: str = Field(description="The presigned download URL")
    expires_in: int = Field(default=60, description="URL expiration time in seconds")
