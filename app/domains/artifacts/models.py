from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Enum as SQLEnum, DateTime, String, Integer
from sqlalchemy.dialects.postgresql import JSONB
from enum import Enum

class ArtifactType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    CODE = "code"
    OTHER = "other"


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(String, primary_key=True, default=lambda: str(uuid7()))
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    message_id = Column(String, ForeignKey("messages.id"), nullable=False)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    type = Column(SQLEnum(ArtifactType), nullable=False)
    artifact_metadata = Column(JSONB)
    file_size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))


