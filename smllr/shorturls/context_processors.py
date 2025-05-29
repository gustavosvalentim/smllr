from django.conf import settings


def feature_settings(request):
    return {
        'allow_social_login': settings.ALLOW_SOCIAL_LOGIN,
        'public_url': settings.PUBLIC_URL,
    }
