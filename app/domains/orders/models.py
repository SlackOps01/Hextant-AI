from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Enum, DateTime, String, Integer
from sqlalchemy.orm import relationship
from enum import Enum

class OrderStatus(str, Enum):
    COMPLETED="completed"
    PENDING="pending"
    FAILED="failed"



class Orders(Base):
    id = Column(String, primary_key=True, default=lambda: str(uuid7()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    tier_id = Column(String, ForeignKey("tiers.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    coupon_id = Column(String, ForeignKey("coupons.id"), nullable=True)
    paystack_reference = Column(String, nullable=True)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    