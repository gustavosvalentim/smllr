from django.urls import path
from smllr.shorturls import views


urlpatterns = [
    path('<str:short_code>', views.ShortURLView.as_view(), name='shorturls_redirect'),
    path('<str:short_code>/details', views.ShortURLDetailsView.as_view(), name='shorturls_details'),
    path('', views.ShortURLFormView.as_view(), name='shorturls_form'),
    path('api/analytics/<str:short_code>', views.AnalyticsAPIView.as_view(), name='shorturls_analytics_api'),
]
