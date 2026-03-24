from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import String, Integer, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domains.orders.models import Orders


class CouponType(str, PyEnum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


class Coupons(Base):
    __tablename__ = "coupons"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid7())
    )
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    type: Mapped[CouponType] = mapped_column(
        Enum(enum=CouponType, name="coupon_type_enum", create_constraint=False),
        nullable=False,
    )
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    max_redemptions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    times_redeemed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    orders: Mapped[list["Orders"]] = relationship("Orders", back_populates="coupon")
