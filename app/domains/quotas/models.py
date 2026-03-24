from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, ForeignKey, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.users.models import User


class ResourceType(str, PyEnum):
    MESSAGE = "message"
    IMAGE = "image"
    RESEARCH = "research"
    DOCUMENT = "document"


class Quotas(Base):
    __tablename__ = "quotas"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid7())
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resource_type: Mapped[ResourceType] = mapped_column(
        Enum(
            ResourceType,
            name="resource_type_enum",
            create_constraint=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        index=True,
    )
    current_usage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    limit: Mapped[int] = mapped_column(Integer, nullable=False)
    reset_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User", back_populates="quotas")
