from django.conf import settings


def settings_processor(request):
    return {
        'allow_social_login': settings.ALLOW_SOCIAL_LOGIN,
    }
