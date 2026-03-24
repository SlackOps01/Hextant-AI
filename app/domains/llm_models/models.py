from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Enum as SQLEnum, DateTime, String, Integer
from sqlalchemy.orm import relationship
from enum import Enum


class ModelType(str, Enum):
    TEXT = "text"
    IMAGE = "image"

class ModelModality(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    MULTIMODAL = "multimodal"





class LanguageModels(Base):
    __tablename__ = "language_models"
    id = Column(String, primary_key=True, default=lambda: str(uuid7()))
    display_name = Column(String, nullable=False)
    model_type = Column(Enum(ModelType), nullable=False)
    modality = Column(SQLEnum(ModelModality), nullable=False)
    context_length = Column(Integer, nullable=False)
    provider = Column(String, nullable=True)
    input_token_price = Column(Integer, nullable=True)
    output_token_price = Column(Integer, nullable=True)
    api_identifier = Column(String, nullable=False, unique=True)
    adapter = Column(String, default="generic")
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))






