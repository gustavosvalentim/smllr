from django.db import models


class Fingerprint(models.Model):
    fingerprint_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Fingerprint at {self.created_at}"
