from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.users.models import User


class AuthSessions(Base):
    __tablename__ = "auth_sessions"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid7())
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_agent: Mapped[str] = mapped_column(String, nullable=False)
    ip_address: Mapped[str] = mapped_column(String, nullable=False)
    device_name: Mapped[str | None] = mapped_column(String, nullable=True)
    device_type: Mapped[str] = mapped_column(String, nullable=False)
    device_os: Mapped[str] = mapped_column(String, nullable=False)
    refresh_token_hash: Mapped[str] = mapped_column(String, nullable=False, index=True)
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, index=True
    )
    session_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user: Mapped["User"] = relationship("User", back_populates="auth_sessions")
