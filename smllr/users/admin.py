from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from smllr.users.models import User


class CustomUserAdmin(UserAdmin):
    """
    Custom admin class for the User model.
    """

    list_display = ('username', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('ip_address',)}),
        (None, {'fields': ('is_anonymous',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('ip_address',)}),
        (None, {'fields': ('is_anonymous',)}),
    )


admin.site.register(User, CustomUserAdmin)
