from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Enum as SQLEnum, DateTime, String
from sqlalchemy.ext.mutable import MutableList, MutableDict
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship
from enum import Enum


class MessageRole(str, Enum):
    USER="user"
    ASSISTANT="assistant"

class MessageType(str, Enum):
    RESEARCH="research"
    TEXT="text"
    IMAGE="image"


class Messages(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid7()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(String, nullable=False)
    message_type = Column(SQLEnum(MessageType), nullable=False, default=MessageType.TEXT)
    message_metadata = Column(JSONB, nullable=True)
    tools = Column(ARRAY(String), nullable=True, default=[])
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
