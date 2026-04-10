from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.domains.users.models import User
from app.domains.subscriptions.schemas import SubscriptionCheckoutRequest, CheckoutResponse, PaymentCallbackRequest
from app.domains.subscriptions.service import SubscriptionService

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: SubscriptionCheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SubscriptionService.create_subscription_checkout(db, current_user.id, request)

@router.post("/verify")
async def verify_payment_post(
    request: PaymentCallbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return await SubscriptionService.verify_payment(db, request)

@router.get("/verify")
async def verify_payment_get(
    reference: str,
    trxref: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Convenience endpoint for frontend to hit after being redirected back from Paystack.
    Paystack appends ?trxref=...&reference=... to the callback URL.
    """
    request = PaymentCallbackRequest(reference=reference)
    return await SubscriptionService.verify_payment(db, request)
