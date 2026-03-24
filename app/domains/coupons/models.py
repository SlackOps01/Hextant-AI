from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, Integer
from enum import Enum

class CouponType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"


class Coupons(Base):
    __tablename__ = "coupons"

    id = Column(String, primary_key=True, default=lambda: str(uuid7()))
    code = Column(String, unique=True, nullable=False, index=True)
    type = Column(SQLEnum(CouponType), nullable=False)
    value = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    max_redemptions = Column(DateTime, nullable=True)
    times_redeemed = Column(DateTime, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
