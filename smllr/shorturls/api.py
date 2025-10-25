from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views import View

from smllr.core.response import not_found
from smllr.shorturls.models import ShortURL, ShortURLClick
from smllr.subscriptions.mixins import ProSubscriptionRequiredMixin
from smllr.users.mixins import NonAnonymousUserRequiredMixin


class AnalyticsAPIView(NonAnonymousUserRequiredMixin, ProSubscriptionRequiredMixin, View):
    def get(self, request: HttpRequest, short_code: str) -> HttpResponse:
        response = HttpResponse()
        short_url = ShortURL.objects.filter(short_code=short_code, user=request.user).first()

        if short_url and short_url.user.pk != request.user.pk:
            response.status_code = 403
            return response

        if not short_url:
            return not_found(request)

        clicks = ShortURLClick.objects.get_analytics_queryset(short_code)
        analytics = {
            "total_clicks": clicks.count(),
        }

        analytics.update(ShortURLClick.objects.get_latest_clicks(short_code))
        analytics.update(ShortURLClick.objects.get_clicks_by_platform(short_code))
        analytics.update(ShortURLClick.objects.get_clicks_by_source(short_code))

        return JsonResponse(analytics)
