import os

from stripe import StripeClient


class SubscriptionManager:
    def __init__(self):
        self.api_key = os.getenv("STRIPE_API_KEY", "")
        self.client = StripeClient(self.api_key)

    def get_customer_by_email(self, email: str) -> str | None:
        response = self.client.v1.customers.list(
            params={
                "email": email,
            }
        )

        if len(response.data) > 0:
            return response.data[0].id

        return None

    def is_subscription_active(self, email: str) -> bool:
        customer_id = self.get_customer_by_email(email)

        if not customer_id:
            return False

        subscriptions = self.client.v1.subscriptions.list(
            params={
                "customer": customer_id,
                "status": "active",
            }
        )

        return len(subscriptions.data) > 0
