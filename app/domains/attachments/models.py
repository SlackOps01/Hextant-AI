from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.messages.models import Messages


class Attachments(Base):
    __tablename__ = "attachments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid7()))
    message_id: Mapped[str] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    file_url: Mapped[str] = mapped_column(String, nullable=False)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mime_type: Mapped[str | None] = mapped_column(String, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    message: Mapped["Messages"] = relationship("Messages", back_populates="attachments")
