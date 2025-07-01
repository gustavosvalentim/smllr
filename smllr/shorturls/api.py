import json

from django.http import HttpRequest, HttpResponse
from django.views import View

from smllr.core.response import not_found
from smllr.shorturls.models import ShortURL, ShortURLClick
from smllr.users.mixins import NonAnonymousUserRequiredMixin


class AnalyticsAPIView(NonAnonymousUserRequiredMixin, View):

    def get(self, request: HttpRequest, short_code: str):
        if short_code is None:
            return not_found(self.request)

        short_url = ShortURL.objects.filter(short_code=short_code).first()
        clicks = ShortURLClick.objects.filter(short_url=short_url).order_by('-clicked_at')

        if not short_url:
            return not_found(self.request)
        
        latest_clicks = []
        for click in clicks[:10]:
            latest_clicks.append({
                'clicked_at': click.clicked_at.isoformat(),
                'user_agent': click.user_agent,
                'ip_address': click.ip_address,
                'device_type': click.device_type,
                'referrer': click.referrer,
            })

        string_response = json.dumps({
            'latest_clicks': latest_clicks,
            'desktop_clicks': clicks.filter(device_type='Desktop').count(),
            'mobile_clicks': clicks.filter(device_type='Mobile').count(),
            'tablet_clicks': clicks.filter(device_type='Tablet').count(),
            'total_clicks': clicks.count(),
        })

        response = HttpResponse()
        response.status_code = 200
        response.content = string_response
        response['Content-Type'] = 'application/json'

        return response
