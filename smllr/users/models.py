from typing import Type

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Enter an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields) -> 'User':
        user = self.create_user(email, password, **extra_fields)
        user.is_anonymous = False
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_anonymous(self, ip_address: str) -> 'User':
        user = self.create_user(
            email=f'anon_{ip_address}@{ip_address}',
            ip_address=ip_address,
            name=ip_address,
            is_anonymous=True,
        )
        user.set_unusable_password()
        user.save()
        return user


class User(AbstractUser):
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_anonymous = models.BooleanField(default=True)

    objects: Type[CustomUserManager] = CustomUserManager()

    username = models.CharField(max_length=50, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
