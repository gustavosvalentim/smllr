from django.db import models


class Fingerprint(models.Model):
    fingerprint_data = models.JSONField()
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.CharField(max_length=512, blank=True, null=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)
    referrer = models.CharField(max_length=512, null=True, blank=True)
    browser_name = models.CharField(max_length=100, null=True, blank=True)
    browser_version = models.CharField(max_length=100, null=True, blank=True)
    os = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fingerprint at {self.created_at}"
