from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from smllr.users.models import User


class CustomUserAdmin(UserAdmin):
    """
    Custom admin class for the User model.
    """

    readonly_fields = (
        "created_at",
        "last_login",
    )
    list_display = (
        "email",
        "ip_address",
        "is_superuser",
        "is_active",
        "is_anonymous",
    )
    search_fields = (
        "email",
        "ip_address",
    )
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("name",)}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_superuser",
                    "is_anonymous",
                )
            },
        ),
        ("Fingerprint", {"fields": ("ip_address",)}),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("ip_address",)}),
        (None, {"fields": ("is_anonymous",)}),
    )


admin.site.register(User, CustomUserAdmin)
