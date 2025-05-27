from django.db import models


class ShortURL(models.Model):
    destination_url = models.URLField()
    short_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    clicks = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.short_code

    def increment_clicks(self):
        self.clicks += 1
        self.save(update_fields=['clicks'])
