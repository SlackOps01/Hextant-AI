from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, Integer, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column


class ModelType(str, PyEnum):
    TEXT = "text"
    IMAGE = "image"


class ModelModality(str, PyEnum):
    TEXT = "text"
    IMAGE = "image"
    MULTIMODAL = "multimodal"


class LanguageModels(Base):
    __tablename__ = "language_models"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid7())
    )
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    model_type: Mapped[ModelType] = mapped_column(
        Enum(enum=ModelType, name="model_type_enum", create_constraint=False),
        nullable=False,
    )
    modality: Mapped[ModelModality] = mapped_column(
        Enum(enum=ModelModality, name="model_modality_enum", create_constraint=False),
        nullable=False,
    )
    context_length: Mapped[int] = mapped_column(Integer, nullable=False)
    provider: Mapped[str | None] = mapped_column(String, nullable=True)
    input_token_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_token_price: Mapped[int | None] = mapped_column(Integer, nullable=True)
    api_identifier: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    adapter: Mapped[str] = mapped_column(String, default="generic")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
