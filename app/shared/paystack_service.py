from app.core.logging import logger
from httpx import AsyncClient
from app.core.config import CONFIG


class PaystackService:
    def __init__(self):
        self.client = AsyncClient(base_url="https://api.paystack.co", timeout=30)

    async def create_plan(self, name: str, amount: int, interval: str):
        """
        Function to create a paystack subscription plan for the hexy equivalent
        
        Name: The name of the plan
        Amount: amount in Naira will be converted in function *100
        interval: monthly, annually, hourly, weekly, quaterly, biannually
        """
        response = await self.client.post(
            url="/plan",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CONFIG.PAYSTACK_SECRET_KEY}"
            },
            json={
                "name": name,
                "amount": amount*100,
                "interval": interval
            }
        )

        logger.info(response.status_code)
        logger.info(response.json())
        response_dict: dict = response.json()

        return response_dict.get("data")['plan_code']


    async def create_subscription(self, email: str, plan_code: str):
        """
        Function to create a paystack subscription for the hexy equivalent
        
        Email: The email of the user
        Plan Code: The plan code of the tier
        """
        response = await self.client.post(
            url="/subscription",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CONFIG.PAYSTACK_SECRET_KEY}"
            },
            json={
                "email": email,
                "plan": plan_code
            }
        )

        logger.info(response.status_code)
        logger.info(response.json())
        response_dict: dict = response.json()

        return response_dict.get("data")

    async def initialize_transaction(self, email: str, amount: int, plan_code: str, callback_url: str | None = None):
        """
        Function to initialize a transaction on Paystack
        
        email: Customer's email
        amount: amount in Naira
        plan_code: Plan to subscribe to
        callback_url: Optional URL to redirect to after payment
        """
        payload = {
            "email": email,
            "amount": amount * 100,
            "plan": plan_code
        }
        if callback_url:
            payload["callback_url"] = callback_url
            
        response = await self.client.post(
            url="/transaction/initialize",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {CONFIG.PAYSTACK_SECRET_KEY}"
            },
            json=payload
        )

        logger.info(response.status_code)
        logger.info(response.json())
        response_dict: dict = response.json()

        return response_dict.get("data")

    async def verify_transaction(self, reference: str):
        """
        Function to verify a Paystack transaction using the reference
        """
        response = await self.client.get(
            url=f"/transaction/verify/{reference}",
            headers={
                "Authorization": f"Bearer {CONFIG.PAYSTACK_SECRET_KEY}"
            }
        )

        logger.info(response.status_code)
        logger.info(response.json())
        response_dict: dict = response.json()

        return response_dict.get("data")