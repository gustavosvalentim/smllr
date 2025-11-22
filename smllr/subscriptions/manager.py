from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import Group
from stripe import StripeClient
from typing import Literal, TypedDict

from smllr.users.models import User


class StripeClientConfiguration(TypedDict):
    secret_key: str


class ProductSubscriptionDetails(TypedDict):
    price_id: str
    price_value: float
    subscription_level: Literal["basic", "pro"]


class CheckoutConfiguration(TypedDict):
    subscriptions: list[ProductSubscriptionDetails]
    post_checkout_redirect_url: str


class SubscriptionManager:
    def __init__(
        self,
        client_configuration: StripeClientConfiguration,
        checkout_configuration: CheckoutConfiguration,
    ):
        self.client_configuration = client_configuration
        self.checkout_configuration = checkout_configuration
        self.client = StripeClient(client_configuration["secret_key"])

    @staticmethod
    def from_settings(client_config_key: str | None = None, checkout_config_key: str | None = None):
        client_config = getattr(settings, client_config_key or "STRIPE_CLIENT")
        checkout_config = getattr(settings, checkout_config_key or "STRIPE_CHECKOUT")
        return SubscriptionManager(client_config, checkout_config)

    def get_customer_by_email(self, email: str) -> str | None:
        response = self.client.v1.customers.list(
            params={
                "email": email,
            }
        )

        if len(response.data) > 0:
            return response.data[0].id

        return None

    def get_subscription_type_by_price(self, price_id: str) -> Literal["basic", "pro"]:
        for price in self.checkout_configuration.get("subscriptions", []):
            if price.get("price_id") == price_id:
                return price.get("subscription_level")
        raise ValueError(f"Price ID {price_id} doesn't exist")

    def get_subscription_by_email(self, email: str) -> dict | None:
        customer_id = self.get_customer_by_email(email)

        if not customer_id:
            return None

        subscriptions = self.client.v1.subscriptions.list(
            params={
                "customer": customer_id,
                "status": "active",
            }
        )

        if len(subscriptions.data) == 0:
            return None

        subscription = subscriptions.data[0]
        price_id = subscription["items"]["data"][0]["price"]["id"]

        subscription_type = self.get_subscription_type_by_price(price_id)

        return {
            "type": subscription_type,
            "amount": subscription["plan"]["amount"] // 100,
            "currency": subscription["plan"]["currency"],
            "started_at": datetime.fromtimestamp(subscription["created"]),
            "billing_cycle": subscription["plan"]["interval"],
        }


class CheckoutManager:
    def __init__(
        self,
        client_configuration: StripeClientConfiguration,
        checkout_configuration: CheckoutConfiguration,
    ):
        self.client_configuration = client_configuration
        self.checkout_configuration = checkout_configuration
        self.client = StripeClient(client_configuration["secret_key"])
        self.subscription_manager = SubscriptionManager(
            client_configuration, checkout_configuration
        )

    @staticmethod
    def from_settings(client_config_key: str | None = None, checkout_config_key: str | None = None):
        client_config = getattr(settings, client_config_key or "STRIPE_CLIENT")
        checkout_config = getattr(settings, checkout_config_key or "STRIPE_CHECKOUT")
        return CheckoutManager(client_config, checkout_config)

    def get_checkout_url(self, subscription_type: str = "basic") -> str:
        post_checkout_redirect_url = self.checkout_configuration.get("post_checkout_redirect_url")
        line_items = []

        for price in self.checkout_configuration.get("subscriptions", []):
            if price.get("subscription_level") == subscription_type:
                line_items.append({"price": price.get("price_id"), "quantity": 1})

        checkout_session = self.client.v1.checkout.sessions.create(
            {
                "line_items": line_items,
                "mode": "subscription",
                "success_url": f"{post_checkout_redirect_url}?session_id={{CHECKOUT_SESSION_ID}}",
            }
        )

        if not checkout_session.url:
            raise Exception("Could not create session")

        return checkout_session.url

    def post_checkout(self, session_id: str):
        session = self.client.v1.checkout.sessions.retrieve(session_id)
        customer = self.client.v1.customers.retrieve(str(session.customer))
        user = User.objects.filter(email=customer.email)

        if not user.exists():
            user = User.objects.create(email=customer.email)
            user.set_unusable_password()
            user.save()

        user = user.first()

        subscription = self.subscription_manager.get_subscription_by_email(str(customer.email))

        if not subscription:
            return

        subscription_group = (
            "BasicSubscriber" if subscription["type"] == "basic" else "ProSubscriber"
        )
        group = Group.objects.filter(name=subscription_group).first()

        user.groups.add(group)
