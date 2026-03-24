from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.enums import Role
from typing import List


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid7())
    )
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[Role] = mapped_column(
        Enum(enum=Role, name="role_enum", create_constraint=False),
        nullable=False,
        default=Role.USER,
    )
    profile_picture_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    auth_sessions: Mapped[List["AuthSessions"]] = relationship(
        "AuthSessions", back_populates="user", cascade="all, delete-orphan"
    )
    conversations: Mapped[List["Conversations"]] = relationship(
        "Conversations", back_populates="user", cascade="all, delete-orphan"
    )
    artifacts: Mapped[List["Artifact"]] = relationship(
        "Artifact", back_populates="owner", cascade="all, delete-orphan"
    )
    subscriptions: Mapped[List["Subscriptions"]] = relationship(
        "Subscriptions", back_populates="user", cascade="all, delete-orphan"
    )
    orders: Mapped[List["Orders"]] = relationship(
        "Orders", back_populates="user", cascade="all, delete-orphan"
    )
    quotas: Mapped[List["Quotas"]] = relationship(
        "Quotas", back_populates="user", cascade="all, delete-orphan"
    )


from app.domains.auth.models import AuthSessions
from app.domains.conversations.models import Conversations
from app.domains.artifacts.models import Artifact
from app.domains.subscriptions.models import Subscriptions
from app.domains.orders.models import Orders
from app.domains.quotas.models import Quotas
