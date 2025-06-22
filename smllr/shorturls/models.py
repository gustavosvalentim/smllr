from datetime import datetime, timedelta
from django.db import models
from django.utils.timezone import make_aware

from smllr.users.models import User


class ShortURL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination_url = models.URLField()
    short_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=150, blank=True, null=True, default='')

    def __str__(self):
        return self.short_code

    def increment_clicks(self):
        self.clicks += 1
        self.save(update_fields=['clicks'])

    def is_expired(self, expiration_time: int) -> bool:
        exp = timedelta(days=expiration_time)
        if self.user.is_anonymous:
            return make_aware(datetime.now()) - self.created_at > exp
        return False


class ShortURLClick(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Click on {self.short_url.short_code} from {self.device_type} at {self.clicked_at}"
