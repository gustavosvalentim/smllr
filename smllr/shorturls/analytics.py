import logging

from datetime import timedelta
from typing import Any

from django.db.models import Count, Q
from django.utils.timezone import now

from smllr.shorturls.models import ShortURL, ShortURLClick


logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for computing URL analytics with optimized queries."""

    def __init__(self, short_url: ShortURL):
        self.short_url = short_url

    def get_comprehensive_analytics(self) -> dict[str, Any]:
        """
        Get all analytics data efficiently with minimal database queries.

        Returns a dictionary containing:
        - total_clicks: Total number of clicks
        - unique_visitors: Count of unique fingerprints
        - clicks_by_day: Daily click counts for last 30 days
        - clicks_by_platform: OS distribution
        - clicks_by_device: Device type distribution
        - clicks_by_browser: Browser distribution
        - clicks_by_source: Referrer distribution
        - latest_clicks: Recent click details
        - peak_hour: Most active hour
        - avg_clicks_per_day: Average daily clicks
        """
        try:
            analytics = {}

            # Get base queryset (last 90 days)
            clicks_qs = ShortURLClick.objects.get_analytics_queryset(
                self.short_url.short_code
            )

            # Basic metrics
            analytics["total_clicks"] = clicks_qs.count()
            analytics["unique_visitors"] = self._get_unique_visitors(clicks_qs)

            # Time-based metrics
            analytics.update(self._get_time_series_data(clicks_qs))
            analytics["peak_hour"] = self._get_peak_hour(clicks_qs)
            analytics["avg_clicks_per_day"] = self._get_avg_clicks_per_day(clicks_qs)

            # Platform and device analytics
            analytics.update(self._get_platform_analytics(clicks_qs))
            analytics.update(self._get_device_analytics(clicks_qs))
            analytics.update(self._get_browser_analytics(clicks_qs))

            # Source/referrer analytics
            analytics.update(self._get_source_analytics(clicks_qs))

            # Latest clicks details
            analytics.update(self._get_latest_clicks(clicks_qs))

            return analytics

        except Exception:
            logger.error(
                f"Error getting analytics for {self.short_url.short_code}",
                exc_info=True,
            )
            # Return minimal analytics on error
            return {
                "total_clicks": self.short_url.clicks,
                "error": "Failed to load detailed analytics",
            }

    def _get_unique_visitors(self, clicks_qs) -> int:
        """Count unique visitors based on fingerprint."""
        return (
            clicks_qs.filter(fingerprint__isnull=False)
            .values("fingerprint")
            .distinct()
            .count()
        )

    def _get_time_series_data(self, clicks_qs) -> dict[str, list[dict[str, Any]]]:
        """Get clicks grouped by day for the last 30 days."""
        thirty_days_ago = now() - timedelta(days=30)

        daily_clicks = (
            clicks_qs.filter(clicked_at__gte=thirty_days_ago)
            .extra(select={"date": "DATE(clicked_at)"})
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        # Fill in missing days with 0 clicks
        clicks_by_day = []
        for i in range(30):
            date = (thirty_days_ago + timedelta(days=i)).date()
            date_str = date.isoformat()
            count = next(
                (
                    item["count"]
                    for item in daily_clicks
                    if str(item["date"]) == date_str
                ),
                0,
            )
            clicks_by_day.append({"date": date_str, "clicks": count})

        return {"clicks_by_day": clicks_by_day}

    def _get_peak_hour(self, clicks_qs) -> int | None:
        """Get the hour with most clicks (0-23)."""
        hourly_clicks = (
            clicks_qs.extra(select={"hour": "EXTRACT(hour FROM clicked_at)"})
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("-count")
            .first()
        )
        return int(hourly_clicks["hour"]) if hourly_clicks else None

    def _get_avg_clicks_per_day(self, clicks_qs) -> float:
        """Calculate average clicks per day over the last 90 days."""
        total = clicks_qs.count()
        return round(total / 90, 2) if total > 0 else 0.0

    def _get_platform_analytics(self, clicks_qs) -> dict[str, dict[str, int]]:
        """Get OS/platform distribution."""
        platform_data = (
            clicks_qs.filter(fingerprint__os__isnull=False)
            .values("fingerprint__os")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Categorize platforms
        windows_clicks = 0
        macos_clicks = 0
        linux_clicks = 0
        android_clicks = 0
        ios_clicks = 0
        other_clicks = 0

        for item in platform_data:
            os_name = item["fingerprint__os"].lower() if item["fingerprint__os"] else ""
            count = item["count"]

            if "windows" in os_name:
                windows_clicks += count
            elif "mac" in os_name or "darwin" in os_name:
                macos_clicks += count
            elif "linux" in os_name:
                linux_clicks += count
            elif "android" in os_name:
                android_clicks += count
            elif "ios" in os_name or "iphone" in os_name or "ipad" in os_name:
                ios_clicks += count
            else:
                other_clicks += count

        return {
            "clicks_by_platform": {
                "windows": windows_clicks,
                "macos": macos_clicks,
                "linux": linux_clicks,
                "android": android_clicks,
                "ios": ios_clicks,
                "other": other_clicks,
            }
        }

    def _get_device_analytics(self, clicks_qs) -> dict[str, dict[str, int]]:
        """Get device type distribution (mobile vs desktop)."""
        device_data = (
            clicks_qs.filter(fingerprint__device_type__isnull=False)
            .values("fingerprint__device_type")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        mobile_clicks = 0
        desktop_clicks = 0
        tablet_clicks = 0
        other_clicks = 0

        for item in device_data:
            device_type = (
                item["fingerprint__device_type"].lower()
                if item["fingerprint__device_type"]
                else ""
            )
            count = item["count"]

            if "mobile" in device_type or "phone" in device_type:
                mobile_clicks += count
            elif "tablet" in device_type or "ipad" in device_type:
                tablet_clicks += count
            elif "desktop" in device_type or "pc" in device_type:
                desktop_clicks += count
            else:
                other_clicks += count

        return {
            "clicks_by_device": {
                "mobile": mobile_clicks,
                "desktop": desktop_clicks,
                "tablet": tablet_clicks,
                "other": other_clicks,
            }
        }

    def _get_browser_analytics(self, clicks_qs) -> dict[str, dict[str, int]]:
        """Get browser distribution."""
        browser_data = (
            clicks_qs.filter(fingerprint__browser_name__isnull=False)
            .values("fingerprint__browser_name")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]  # Top 10 browsers
        )

        browsers = {}
        for item in browser_data:
            browser_name = item["fingerprint__browser_name"] or "Unknown"
            browsers[browser_name] = item["count"]

        return {"clicks_by_browser": browsers}

    def _get_source_analytics(self, clicks_qs) -> dict[str, Any]:
        """Get referrer/source distribution."""
        referrer_data = (
            clicks_qs.filter(fingerprint__referrer__isnull=False)
            .exclude(fingerprint__referrer="")
            .values("fingerprint__referrer")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        # Categorize referrers
        direct_clicks = clicks_qs.filter(
            Q(fingerprint__referrer__isnull=True) | Q(fingerprint__referrer="")
        ).count()

        social_media = {
            "facebook": 0,
            "instagram": 0,
            "twitter": 0,
            "linkedin": 0,
            "reddit": 0,
            "tiktok": 0,
        }

        search_engines = {
            "google": 0,
            "bing": 0,
            "yahoo": 0,
        }

        other_referrers = []

        for item in referrer_data:
            referrer = (
                item["fingerprint__referrer"].lower()
                if item["fingerprint__referrer"]
                else ""
            )
            count = item["count"]

            # Check social media
            matched = False
            for social in social_media:
                if social in referrer:
                    social_media[social] += count
                    matched = True
                    break

            if matched:
                continue

            # Check search engines
            for engine in search_engines:
                if engine in referrer:
                    search_engines[engine] += count
                    matched = True
                    break

            if not matched:
                other_referrers.append(
                    {"referrer": item["fingerprint__referrer"], "clicks": count}
                )

        return {
            "clicks_by_source": {
                "direct": direct_clicks,
                "social_media": social_media,
                "search_engines": search_engines,
                "other_referrers": other_referrers[:10],  # Top 10 other referrers
            }
        }

    def _get_latest_clicks(self, clicks_qs) -> dict[str, list[dict[str, str]]]:
        """Get recent click details (last 50)."""
        latest_clicks = clicks_qs.select_related("fingerprint")[:50]

        clicks_list = []
        for click in latest_clicks:
            if click.fingerprint:
                clicks_list.append(
                    {
                        "clicked_at": click.clicked_at.strftime("%Y-%m-%d %H:%M:%S"),
                        "ip_address": click.fingerprint.ip_address or "Unknown",
                        "device_type": click.fingerprint.device_type or "Unknown",
                        "os": click.fingerprint.os or "Unknown",
                        "browser": f"{click.fingerprint.browser_name or 'Unknown'} {click.fingerprint.browser_version or ''}".strip(),
                        "referrer": click.fingerprint.referrer or "Direct",
                    }
                )

        return {"latest_clicks": clicks_list}
