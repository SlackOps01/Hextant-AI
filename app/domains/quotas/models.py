from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import Column, String, Enum as SQLEnum, DateTime
from enum import Enum

class ResourceType(str, Enum):
    MESSAGE = "message"
    IMAGE = "image"
    RESEARCH = "research"
    DOCUMENT = "document"


class Quotas(Base):
    __tablename__ = "quotas"

    id = Column(String, primary_key=True, default=lambda: str(uuid7()))
    user_id = Column(String, index=True, nullable=False)
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    current_usage = Column(DateTime, default=0, nullable=False)
    limit = Column(DateTime, nullable=False)
    reset_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
