from django.db import models


class User(models.Model):
    ip_address = models.GenericIPAddressField()
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ShortURL(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    destination_url = models.URLField()
    short_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.short_code

    def increment_clicks(self):
        self.clicks += 1
        self.save(update_fields=['clicks'])


class ShortURLClick(models.Model):
    short_url = models.ForeignKey(ShortURL, on_delete=models.CASCADE)
    clicked_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Click on {self.short_url.short_code} at {self.clicked_at}"
