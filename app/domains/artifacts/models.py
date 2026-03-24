from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, ForeignKey, DateTime, Integer, Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.users.models import User
    from app.domains.messages.models import Messages


class ArtifactType(str, PyEnum):
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    CODE = "code"
    OTHER = "other"


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid7())
    )
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    message_id: Mapped[str] = mapped_column(
        ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[ArtifactType] = mapped_column(
        Enum(
            ArtifactType,
            name="artifact_type_enum",
            create_constraint=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        index=True,
    )
    artifact_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True
    )

    owner: Mapped["User"] = relationship("User", back_populates="artifacts")
    message: Mapped["Messages"] = relationship("Messages", back_populates="artifacts")
