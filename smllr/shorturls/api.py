import json

from django.http import HttpRequest, HttpResponse
from django.views import View

from smllr.core.response import not_found
from smllr.shorturls.models import ShortURL, ShortURLClick
from smllr.users.mixins import NonAnonymousUserRequiredMixin


class AnalyticsAPIView(NonAnonymousUserRequiredMixin, View):
    def get(self, request: HttpRequest, short_code: str) -> HttpResponse:
        short_url_exists = ShortURL.objects.filter(short_code=short_code).exists()

        if not short_url_exists:
            return not_found(request)

        clicks = ShortURLClick.objects.get_queryset(short_code)
        analytics = {
            "total_clicks": clicks.count(),
        }

        analytics.update(ShortURLClick.objects.get_latest_clicks(short_code))
        analytics.update(ShortURLClick.objects.get_clicks_by_platform(short_code))
        analytics.update(ShortURLClick.objects.get_clicks_by_source(clicks))

        response = HttpResponse()
        response.status_code = 200
        response.content = json.dumps(analytics)
        response["Content-Type"] = "application/json"

        return response
