from datetime import datetime, timedelta

from django.db import models
from django.db.models.manager import Manager
from django.conf import settings
from django.utils.timezone import make_aware, now
from django.utils.translation import gettext as _

from smllr.fingerprint.models import Fingerprint
from smllr.shorturls.helpers import generate_short_code
from smllr.users.models import User


class ShortURLManager(Manager):
    def create(
        self, user: User, destination_url: str, name: str, short_code: str | None = None
    ) -> "ShortURL":
        if user.is_anonymous:
            if (
                ShortURL.objects.filter(user=user).count()
                >= settings.MAX_SHORTURLS_PER_ANON_USER
            ):
                raise Exception(_("You've reached your limit of URLs."))

        if short_code is None or short_code == "":
            short_code = generate_short_code()

        return super().create(
            user=user, destination_url=destination_url, name=name, short_code=short_code
        )


class ShortURL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination_url = models.URLField()
    short_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=150, blank=True, null=True, default="")

    objects: ShortURLManager = ShortURLManager()

    class Meta:
        permissions = [("view_shorturl_analytics", "View Short URL analytics")]
        indexes = [
            models.Index(
                fields=["user", "-created_at"], name="shorturl_user_created_idx"
            ),
            models.Index(fields=["short_code"], name="shorturl_code_idx"),
        ]

    def __str__(self):
        return f"{self.name} - {self.short_code}"

    def increment_clicks(self):
        self.clicks += 1
        self.save(update_fields=["clicks"])

    def is_expired(self) -> bool:
        expiration = timedelta(days=settings.SHORTURL_EXPIRATION_TIME_DAYS)
        if self.user.is_anonymous:
            return make_aware(datetime.now()) - self.created_at > expiration
        return False


class ShortURLClickManager(Manager):
    def get_analytics_queryset(
        self, short_code: str
    ) -> models.QuerySet["ShortURLClick"]:
        """Get clicks for a short code within the last 90 days."""
        return self.filter(
            short_url__short_code=short_code,
            clicked_at__gte=now() - timedelta(days=90),
        ).order_by("-clicked_at")

    def get_latest_clicks(
        self, short_code: str, limit: int = 50
    ) -> dict[str, list[dict[str, str]]]:
        """
        Get latest clicks with fingerprint details.

        DEPRECATED: Use AnalyticsService for comprehensive analytics.
        Kept for backward compatibility.
        """
        clicks = self.get_analytics_queryset(short_code).select_related("fingerprint")[
            :limit
        ]
        latest_clicks = []
        for click in clicks:
            if click.fingerprint:
                latest_clicks.append(
                    {
                        "clicked_at": click.clicked_at.strftime("%Y/%m/%d"),
                        "user_agent": click.fingerprint.user_agent or "Unknown",
                        "ip_address": click.fingerprint.ip_address or "Unknown",
                        "device_type": click.fingerprint.device_type or "Unknown",
                        "referrer": click.fingerprint.referrer or "Direct",
                        "os": click.fingerprint.os or "Unknown",
                        "browser_name": click.fingerprint.browser_name or "Unknown",
                        "browser_version": click.fingerprint.browser_version or "",
                    }
                )

        return {
            "latest_clicks": latest_clicks,
        }

    def get_clicks_by_platform(self, short_code: str) -> dict[str, int]:
        """
        Get basic platform statistics.

        DEPRECATED: Use AnalyticsService for comprehensive analytics.
        Kept for backward compatibility.
        """
        clicks = self.get_analytics_queryset(short_code)
        return {
            "windows_clicks": clicks.filter(
                fingerprint__os__icontains="Windows"
            ).count(),
            "linux_clicks": clicks.filter(fingerprint__os__icontains="Linux").count(),
            "android_clicks": clicks.filter(
                fingerprint__os__icontains="Android"
            ).count(),
        }

    def get_clicks_by_source(self, short_code: str) -> dict[str, int]:
        """
        Get basic referrer statistics.

        DEPRECATED: Use AnalyticsService for comprehensive analytics.
        Kept for backward compatibility.
        """
        clicks = self.get_analytics_queryset(short_code)
        return {
            "instagram_clicks": clicks.filter(
                fingerprint__referrer__icontains="instagram"
            ).count(),
            "facebook_clicks": clicks.filter(
                fingerprint__referrer__icontains="facebook"
            ).count(),
        }


class ShortURLClick(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True)
    fingerprint = models.ForeignKey(
        Fingerprint, on_delete=models.DO_NOTHING, blank=True, null=True
    )

    objects = ShortURLClickManager()

    class Meta:
        indexes = [
            models.Index(
                fields=["short_url", "-clicked_at"], name="click_url_time_idx"
            ),
            models.Index(fields=["fingerprint"], name="click_fingerprint_idx"),
        ]
