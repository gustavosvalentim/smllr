from django.contrib import admin

from smllr.shorturls.models import ShortURL, ShortURLClick


class ShortURLClickInline(admin.TabularInline):
    model = ShortURLClick
    readonly_fields = (
        "short_url",
        "clicked_at",
        "fingerprint",
    )


class ShortURLAdmin(admin.ModelAdmin):
    readonly_fields = (
        "created_at",
        "clicks",
    )
    list_display = (
        "short_code",
        "destination_url",
        "user",
        "clicks",
        "created_at",
    )
    search_fields = (
        "short_code",
        "destination_url",
        "user__email",
    )
    fieldsets = (
        (
            "Details",
            {
                "fields": (
                    "user",
                    "name",
                    "destination_url",
                    "short_code",
                )
            },
        ),
        ("Analytics", {"fields": ("clicks",)}),
        ("Timestamps", {"fields": ("created_at",)}),
    )
    inlines = [ShortURLClickInline]


admin.site.register(ShortURL, ShortURLAdmin)
