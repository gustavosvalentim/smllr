from django.contrib import admin
from django.contrib.auth.admin import Group, UserAdmin

from smllr.users.forms import GroupAdminForm
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
        "is_guest_user",
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
                    "is_guest_user",
                )
            },
        ),
        ("Fingerprint", {"fields": ("ip_address",)}),
        ("Important dates", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {"fields": ("ip_address",)}),
        (None, {"fields": ("is_guest_user",)}),
    )


admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Group)


class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    filter_horizontal = ["permissions"]


admin.site.register(Group, GroupAdmin)
