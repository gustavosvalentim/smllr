from datetime import datetime, timedelta

from django.db import models
from django.db.models.manager import Manager
from django.conf import settings
from django.utils.timezone import make_aware
from django.utils.translation import gettext as _

from smllr.fingerprint.models import Fingerprint
from smllr.shorturls.helpers import generate_short_code
from smllr.users.models import User


class ShortURLManager(Manager):
    
    def create(self, user: User, destination_url: str, name: str, short_code: str = None) -> 'ShortURL':
        if user.is_anonymous:
            if ShortURL.objects.filter(user=user).count() >= settings.MAX_SHORTURLS_PER_ANON_USER:
                raise Exception(_("You've reached your limit of URLs."))

        if short_code is None or short_code == '':
            short_code = generate_short_code()

        return super().create(user=user, destination_url=destination_url, name=name, short_code=short_code)


class ShortURL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination_url = models.URLField()
    short_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.PositiveIntegerField(default=0)
    name = models.CharField(max_length=150, blank=True, null=True, default='')

    objects: ShortURLManager = ShortURLManager()

    def __str__(self):
        return self.short_code

    def increment_clicks(self):
        self.clicks += 1
        self.save(update_fields=['clicks'])

    def is_expired(self) -> bool:
        expiration = timedelta(days=settings.SHORTURL_EXPIRATION_TIME_DAYS)
        if self.user.is_anonymous:
            return make_aware(datetime.now()) - self.created_at > expiration
        return False


class ShortURLClick(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    fingerprint = models.ForeignKey(Fingerprint, blank=True, null=True)

    def __str__(self):
        return f"Click on {self.short_url.short_code} from {self.device_type} at {self.clicked_at}"
