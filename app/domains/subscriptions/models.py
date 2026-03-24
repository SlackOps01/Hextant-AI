from app.core.database import Base
from uuid import uuid7
from datetime import datetime, timezone
from sqlalchemy import Column, ForeignKey, Enum, DateTime, String
from sqlalchemy.orm import relationship

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    EXPIRED = "expired"
    PENDING = "pending"



class Subscriptions(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid7()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    order_id = Column(String, ForeignKey("orders.id"), nullable=False)
    subscription_id = Column(String, nullable=False)
    tier_id = Column(String, ForeignKey("tiers.id"), nullable=False)
    status = Column(Enum(SubscriptionStatus), nullable=False)
    current_period_start = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    current_period_end = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False)



