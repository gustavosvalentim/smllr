from typing import Type

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):

    def create_anonymous(self, ip_address: str) -> 'User':
        user = self.model(ip_address=ip_address, name=ip_address, is_anonymous=True)
        user.set_unusable_password()
        user.save()
        return user


class User(AbstractUser):
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=True)

    objects: Type[CustomUserManager] = CustomUserManager()

    def __str__(self):
        return ' - '.join([self.name, self.email])
