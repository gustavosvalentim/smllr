import logging

from django.http import HttpRequest, JsonResponse
from django.views import View

from smllr.core.response import not_found
from smllr.shorturls.analytics import AnalyticsService
from smllr.shorturls.models import ShortURL
from smllr.subscriptions.mixins import ProSubscriptionRequiredMixin
from smllr.users.mixins import NonAnonymousUserRequiredMixin


logger = logging.getLogger(__name__)


class AnalyticsAPIView(
    NonAnonymousUserRequiredMixin, ProSubscriptionRequiredMixin, View
):
    """
    API endpoint for retrieving comprehensive URL analytics.

    Requires:
    - Authenticated user (non-anonymous)
    - Pro subscription

    Returns:
    - JSON response with comprehensive analytics including:
      - Total clicks and unique visitors
      - Time series data (clicks by day)
      - Platform, device, and browser distributions
      - Source/referrer analytics
      - Latest click details
      - Peak usage times
    """

    def get(self, request: HttpRequest, short_code: str) -> JsonResponse:
        """Get comprehensive analytics for a short URL."""
        try:
            # Get short URL and verify ownership
            short_url = ShortURL.objects.filter(
                short_code=short_code, user_id=request.user.pk
            ).first()

            if not short_url:
                return not_found(request)

            # Initialize analytics service and get comprehensive data
            analytics_service = AnalyticsService(short_url)
            analytics = analytics_service.get_comprehensive_analytics()

            # Add short URL metadata
            analytics["short_url"] = {
                "code": short_url.short_code,
                "name": short_url.name,
                "destination_url": short_url.destination_url,
                "created_at": short_url.created_at.isoformat(),
            }

            return JsonResponse(analytics)

        except Exception:
            logger.error(f"Error retrieving analytics for {short_code}", exc_info=True)
            return JsonResponse({"error": "Failed to retrieve analytics"}, status=500)
