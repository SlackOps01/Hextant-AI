from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.messages.models import Messages


class MemoryCategory(str, PyEnum):
    FACT = "fact"
    PREFERENCE = "preference"
    EXPERIENCE = "experience"
    OTHER = "other"


class Memories(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid7())
    )
    source_message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[MemoryCategory] = mapped_column(
        Enum(enum=MemoryCategory, name="memory_category_enum", create_constraint=False),
        nullable=False,
        default=MemoryCategory.OTHER,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    source_message: Mapped["Messages"] = relationship(
        "Messages", back_populates="memories"
    )
