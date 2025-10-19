from django.conf import settings


def conf(request):
    return {
        "settings": {
            "public_url": settings.PUBLIC_URL,
        }
    }
