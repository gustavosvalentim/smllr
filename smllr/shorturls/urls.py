from django.urls import path
from smllr.shorturls import views


urlpatterns = [
    path('<str:short_code>', views.ShortURLView.as_view(), name='shorturls_redirect'),
    path('', views.ShortURLFormView.as_view(), name='shorturls_form'),
    path('analytics/<str:short_code>', views.ShortURLDetailsView.as_view(), name='shorturls_details'),
]
