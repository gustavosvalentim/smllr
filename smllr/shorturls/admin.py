from django.contrib import admin

from smllr.shorturls.models import ShortURL, ShortURLClick


admin.site.register(ShortURL)
admin.site.register(ShortURLClick)
