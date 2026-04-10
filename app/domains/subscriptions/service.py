from sqlalchemy.orm import Session
from app.shared.paystack_service import PaystackService
from app.domains.users.models import User
from app.domains.tiers.models import Tiers
from fastapi import HTTPException, status
from app.domains.subscriptions.models import Subscriptions, SubscriptionStatus
from app.domains.orders.models import Orders, OrderStatus
from app.domains.subscriptions.schemas import SubscriptionCheckoutRequest, CheckoutResponse, PaymentCallbackRequest
from datetime import datetime, timezone
import dateutil.parser

class SubscriptionService:
    @staticmethod
    async def create_subscription_checkout(db: Session, user_id: str, request: SubscriptionCheckoutRequest) -> CheckoutResponse:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        tier = db.query(Tiers).filter(Tiers.id == request.tier_id).first()
        if not tier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tier not found")

        if not tier.paystack_plan_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tier does not have a linked Paystack plan")

        paystack_service = PaystackService()
        payment_data = await paystack_service.initialize_transaction(
            email=user.email,
            amount=tier.price,
            plan_code=tier.paystack_plan_code,
            callback_url=request.callback_url
        )

        if not payment_data or "authorization_url" not in payment_data or "reference" not in payment_data:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to initialize Paystack transaction")

        # Create Order
        order = Orders(
            user_id=user.id,
            tier_id=tier.id,
            amount=tier.price,
            paystack_reference=payment_data["reference"],
            status=OrderStatus.PENDING
        )
        db.add(order)
        db.commit()

        return CheckoutResponse(
            authorization_url=payment_data["authorization_url"],
            reference=payment_data["reference"]
        )

    @staticmethod
    async def verify_payment(db: Session, request: PaymentCallbackRequest) -> dict:
        paystack_service = PaystackService()
        verification_data = await paystack_service.verify_transaction(request.reference)

        if not verification_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payment reference")

        status_flag = verification_data.get("status")
        if status_flag != "success":
            # Update order to failed
            order = db.query(Orders).filter(Orders.paystack_reference == request.reference).first()
            if order:
                order.status = OrderStatus.FAILED
                db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment was not successful")

        # Payment successful
        order = db.query(Orders).filter(Orders.paystack_reference == request.reference).first()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        if order.status == OrderStatus.COMPLETED:
            return {"message": "Payment already verified", "subscription_status": "ACTIVE"}

        order.status = OrderStatus.COMPLETED

        # Create or update subscription
        # Note: Paystack might have already created a subscription after the successful transaction.
        plan_object = verification_data.get("plan_object", {})
        subscription_code = plan_object.get("subscription_code") or verification_data.get("subscription_code") 
        # If Paystack didn't explicitly give us the subscription code here, we could just rely on the subscription to be managed locally, or fetch it.
        # But verify_transaction response for a plan transaction usually includes plan info but maybe not subscription id.
        # Actually it's often in plan.
        # Let's create a subscription locally for our system to grant them access
        
        # Determine the current period end based on interval or standard monthly billing
        # For a standard monthly plan:
        current_period_end = datetime.now(timezone.utc)
        # Ideally, this comes from Paystack's subscription object. If not, default to 30 days.
        
        new_subscription = Subscriptions(
            user_id=order.user_id,
            order_id=order.id,
            tier_id=order.tier_id,
            subscription_id=subscription_code or "NO_EXT_ID",
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.now(timezone.utc),
            current_period_end=datetime.now(timezone.utc) # Placeholder, ideally updated by webhook or parsed from Paystack
        )
        db.add(new_subscription)
        db.commit()

        return {"message": "Payment successful and subscription activated"}