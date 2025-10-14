import json

from django.http import HttpRequest, HttpResponse
from django.views import View

from smllr.core.response import not_found
from smllr.shorturls.models import ShortURL, ShortURLClick
from smllr.users.mixins import NonAnonymousUserRequiredMixin


class AnalyticsAPIView(NonAnonymousUserRequiredMixin, View):

    def _get_latest_clicks(self, clicks: list[ShortURLClick]):
        latest_clicks = []
        for click in clicks[:10]:
            latest_clicks.append({
                'clicked_at': click.clicked_at.strftime("%Y/%m/%d"),
                'user_agent': click.fingerprint.user_agent,
                'ip_address': click.fingerprint.ip_address,
                'device_type': click.fingerprint.device_type,
                'referrer': click.fingerprint.referrer,
                'os': click.fingerprint.os,
                'browser_name': click.fingerprint.browser_name,
                'browser_version': click.fingerprint.browser_version,
            })

        return {
            'latest_clicks': latest_clicks,
        }

    def _get_clicks_by_platform(self, clicks: list[ShortURLClick]):
        return {
            'windows_clicks': clicks.filter(fingerprint__os__contains='windows').count(),
            'linux_clicks': clicks.filter(fingerprint__os__contains='linux').count(),
            'android_clicks': clicks.filter(fingerprint__os__contains='android').count(),
        }

    def _get_clicks_by_source(self, clicks: list[ShortURLClick]):
        return {
            'instagram_clicks': clicks.filter(fingerprint__referrer__contains='instagram').count(),
            'facebook_clicks': clicks.filter(fingerprint__referrer__contains='facebook').count(),
        }

    def get(self, request: HttpRequest, short_code: str):
        short_url = ShortURL.objects.filter(short_code=short_code).first()

        if not short_url:
            return not_found(request)

        clicks = ShortURLClick.objects.filter(short_url=short_url).order_by('-clicked_at')
        analytics = {
            'latest_clicks': self._get_latest_clicks(clicks),
            'total_clicks': clicks.count(),
        }

        analytics.update(self._get_latest_clicks(clicks))
        analytics.update(self._get_clicks_by_platform(clicks))
        analytics.update(self._get_clicks_by_source(clicks))

        response = HttpResponse()
        response.status_code = 200
        response.content = json.dumps(analytics) 
        response['Content-Type'] = 'application/json'

        return response
