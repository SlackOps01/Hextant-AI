from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Enum as SQLEnum, DateTime, String, Boolean
from sqlalchemy.orm import relationship

class AuthSessions(Base):
    __tablename__ = "auth_sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid7()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user_agent = Column(String, nullable=False)
    ip_address = Column(String, nullable=False)
    device_name = Column(String, nullable=True)
    device_type = Column(String, nullable=False)
    device_os = Column(String, nullable=False)
    refresh_token_hash = Column(String, nullable=False)
    is_revoked = Column(Boolean, nullable=False, default=False)
    session_expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))