from allauth.socialaccount.models import SocialAccount
from django.conf import settings


def social_account(request):
    context = {"socialaccount": {}}

    if not request.user or request.user.pk is None:
        return context

    socialaccount = SocialAccount.objects.filter(user=request.user).first()
    if not socialaccount:
        return context

    return {"socialaccount": {"picture": socialaccount.extra_data.get("picture")}}


def feature_toggle(request):
    return {
        "feature_toggle": {
            "allow_social_login": settings.ALLOW_SOCIAL_LOGIN,
        }
    }
