from django.shortcuts import redirect
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.views.generic import TemplateView
from smllr.subscriptions.manager import CheckoutManager, SubscriptionManager
from smllr.users.mixins import NonAnonymousUserRequiredMixin


@method_decorator(csrf_exempt, name="dispatch")
class CheckoutView(View, NonAnonymousUserRequiredMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkout_manager = CheckoutManager.from_settings()

    def get(self, request: HttpRequest):
        checkout_url = self.checkout_manager.get_checkout_url()
        return redirect(checkout_url, permanent=True)


class PostCheckoutView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.checkout_manager = CheckoutManager.from_settings()

    def get(self, request: HttpRequest):
        self.checkout_manager.post_checkout(str(request.GET.get("session_id")))
        return redirect("/", permanent=True)


class SubscriptionSettingsView(TemplateView, NonAnonymousUserRequiredMixin):
    template_name = "subscriptions/subscriptions_settings.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscription_manager = SubscriptionManager.from_settings()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscription = self.subscription_manager.get_subscription_by_email(
            self.request.user.email
        )
        context.update({"subscription": subscription})
        return context
