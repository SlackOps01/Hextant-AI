from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.subscriptions.models import Subscriptions
    from app.domains.orders.models import Orders


class Tiers(Base):
    __tablename__ = "tiers"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid7())
    )
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    message_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    image_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    research_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    document_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    model_access: Mapped[list[str]] = mapped_column(
        ARRAY(String), nullable=False, default=[]
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    subscriptions: Mapped[list["Subscriptions"]] = relationship(
        "Subscriptions", back_populates="tier"
    )
    orders: Mapped[list["Orders"]] = relationship("Orders", back_populates="tier")
