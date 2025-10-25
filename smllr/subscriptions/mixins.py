from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse


class SubscriptionRequiredMixin(UserPassesTestMixin):
    subscription_group = "Subscriber"

    def test_func(self):
        return self.request.user.groups.filter(name=self.subscription_group).exists()

    def handle_no_permission(self):
        response = HttpResponse()
        response.status_code = 401
        return response


class BasicSubscriptionRequiredMixin(SubscriptionRequiredMixin):
    subscription_group = "BasicSubscriber"


class ProSubscriptionRequiredMixin(SubscriptionRequiredMixin):
    subscription_group = "ProSubscriber"
