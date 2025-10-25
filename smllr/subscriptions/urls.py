from django.urls import path
from smllr.subscriptions import views


urlpatterns = [
    path("checkout", views.CheckoutView.as_view(), name="create-checkout-session"),
    path("post-checkout", views.PostCheckoutView.as_view(), name="post-checkout"),
    path("settings", views.SubscriptionSettingsView.as_view(), name="subscription-settings"),
]
