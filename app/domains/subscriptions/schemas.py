from pydantic import BaseModel
from typing import Optional

class SubscriptionCheckoutRequest(BaseModel):
    tier_id: str
    callback_url: Optional[str] = None

class CheckoutResponse(BaseModel):
    authorization_url: str
    reference: str

class PaymentCallbackRequest(BaseModel):
    reference: str
