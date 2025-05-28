from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=True)

    def __str__(self):
        return str(self.pk)
