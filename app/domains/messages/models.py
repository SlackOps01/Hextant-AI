from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.conversations.models import Conversations


class MessageRole(str, PyEnum):
    USER = "user"
    ASSISTANT = "assistant"


class MessageType(str, PyEnum):
    RESEARCH = "research"
    TEXT = "text"
    IMAGE = "image"


class Messages(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid7())
    )
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[MessageRole] = mapped_column(
        Enum(enum=MessageRole, name="message_role_enum", create_constraint=False),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(String, nullable=False)
    message_type: Mapped[MessageType] = mapped_column(
        Enum(enum=MessageType, name="message_type_enum", create_constraint=False),
        nullable=False,
        default=MessageType.TEXT,
    )
    message_metadata: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tools: Mapped[list[str] | None] = mapped_column(
        ARRAY(String), nullable=True, default=[]
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    conversation: Mapped["Conversations"] = relationship(
        "Conversations", back_populates="messages"
    )
    memories: Mapped[list["Memories"]] = relationship(
        "Memories", back_populates="source_message", cascade="all, delete-orphan"
    )
    artifacts: Mapped[list["Artifact"]] = relationship(
        "Artifact", back_populates="message", cascade="all, delete-orphan"
    )


from app.domains.memories.models import Memories
from app.domains.artifacts.models import Artifact
