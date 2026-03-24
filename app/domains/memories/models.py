from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Enum as SQLEnum, DateTime, String
from sqlalchemy.orm import relationship
from enum import Enum

class MemoryCategory(str, Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    EXPERIENCE = "experience"
    OTHER = "other"


class Memories(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, default=lambda: str(uuid7()))
    source_message_id = Column(String, ForeignKey("messages.id"), nullable=False)
    content = Column(String, nullable=False)
    category = Column(SQLEnum(MemoryCategory), nullable=False, default=MemoryCategory.OTHER)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
