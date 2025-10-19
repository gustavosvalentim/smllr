from django.urls import path

from smllr.shorturls import views
from smllr.shorturls import api


urlpatterns = [
    path(
        "<str:short_code>",
        views.ShortURLRedirectView.as_view(),
        name="shorturls_redirect",
    ),
    path(
        "<str:short_code>/details",
        views.ShortURLDetailsView.as_view(),
        name="shorturls_details",
    ),
    path("", views.ShortURLFormView.as_view(), name="shorturls_form"),
    path(
        "api/analytics/<str:short_code>",
        api.AnalyticsAPIView.as_view(),
        name="shorturls_analytics_api",
    ),
]
