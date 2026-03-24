from sqlalchemy.dialects.postgresql import ARRAY
from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean


class Tiers(Base):
    __tablename__ = "tiers"

    id = Column(String, primary_key=True, default=lambda: str(uuid7()))
    name = Column(String, unique=True, nullable=False)
    price = Column(Integer, nullable=False)
    message_limit = Column(Integer, nullable=False)
    image_limit = Column(Integer, nullable=False)
    research_limit = Column(Integer, nullable=False)
    document_limit = Column(Integer, nullable=False)
    model_access = Column(ARRAY(String), nullable=False, default=[])
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))